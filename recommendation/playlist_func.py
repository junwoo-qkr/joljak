import random
import requests
import time
import re
from django.conf import settings
from googleapiclient.errors import HttpError
from recommendation.models import music_list
from .youtube_utils import (
    get_youtube_service, create_playlist,
    extract_video_id, search_video, add_video_to_playlist
)


def safe_add_video(service, playlist_id, video_id, retries=3, delay=2):
    """
    유튜브 API 호출 시 SERVICE_UNAVAILABLE 또는 Conflict 에러 발생 시 재시도 로직을 수행합니다.
    """
    for attempt in range(retries):
        try:
            add_video_to_playlist(service, playlist_id, video_id)
            return True
        except HttpError as e:
            status = e.resp.status
            # 일시적 서비스 장애 또는 충돌 오류시 재시도
            if status in (409, 503):
                time.sleep(delay * (2 ** attempt))  # 지수 백오프
                continue
            # 다른 에러는 상위로 전달
            raise
    return False


def get_similar_tracks(title, artist, limit=3):
    """
    Last.fm API를 이용해 주어진 제목과 아티스트의 유사 트랙을 반환하며
    track.getInfo를 통해 앨범명과 발매년도를 함께 가져옵니다.
    """
    api_url = 'http://ws.audioscrobbler.com/2.0/'
    # 1) 유사 트랙 조회
    sim_params = {
        'method': 'track.getSimilar',
        'track': title,
        'artist': artist,
        'api_key': settings.LASTFM_API_KEY,
        'format': 'json',
        'limit': limit
    }
    try:
        sim_resp = requests.get(api_url, params=sim_params)
        sim_resp.raise_for_status()
        tracks = sim_resp.json().get('similartracks', {}).get('track', [])
    except Exception:
        tracks = []

    results = []
    # 2) 개별 트랙 상세 정보 조회 (앨범, 발매년도)
    for t in tracks:
        t_title = t.get('name')
        t_artist = t.get('artist', {}).get('name')
        album = ''
        year = ''
        info_params = {
            'method': 'track.getInfo',
            'track': t_title,
            'artist': t_artist,
            'api_key': settings.LASTFM_API_KEY,
            'format': 'json'
        }
        try:
            info_resp = requests.get(api_url, params=info_params)
            info_resp.raise_for_status()
            info = info_resp.json().get('track', {})
            album = info.get('album', {}).get('title', '')
            published = info.get('wiki', {}).get('published', '')
            if published:
                match = re.search(r"\b(\d{4})\b", published)
                if match:
                    year = match.group(1)
        except Exception:
            # 상세 정보가 없거나 요청 실패 시 빈 문자열 유지
            pass


        results.append({
            'title': t_title,
            'artist': t_artist,
            'album': album,
            'year': year
        })
    return results


def get_playlist(request, e, y, n, similar_limit=None, max_total=20):
    """
    감정(e), 발매연도(y), 국가(n)에 맞게 기본 5곡을 추출하고,
    Last.fm API 유사곡을 가져와 최대 max_total 곡까지
    YouTube 플레이리스트를 생성해 반환합니다.
    """
    # 감정 코드 매핑
    emotion_dict = {
        'Delighted': 0, 'Happy': 1, 'Anxious': 2,
        'Angry': 3, 'Depressed': 4, 'Tired': 5,
        'Calm': 6, 'Satisfied': 7
    }
    emo_code = emotion_dict.get(e[0])
    qs = music_list.objects.filter(nation__in=n, y__in=y, sector=emo_code)

    if not qs.exists():
        return [], [], [], [], ''

    # 샘플 5곡 추출
    sample_qs = qs.order_by('?')[:5]
    titles = [m.title for m in sample_qs]
    artists = [m.artist for m in sample_qs]
    albums = [m.album for m in sample_qs]
    years = [m.year for m in sample_qs]
    links = [m.link for m in sample_qs]

    # 추천 곡 개수 설정
    if similar_limit is None:
        similar_limit = getattr(settings, 'LASTFM_SIMILAR_LIMIT', 3)

    # 추천 API로 유사 곡 가져와 메타데이터 포함해 추가
    seen = set(zip(titles, artists))
    for title_, artist_ in zip(titles.copy(), artists.copy()):
        for rec in get_similar_tracks(title_, artist_, limit=similar_limit):
            pair = (rec['title'], rec['artist'])
            if pair in seen:
                continue
            seen.add(pair)
            titles.append(rec['title'])
            artists.append(rec['artist'])
            albums.append(rec.get('album', ''))
            years.append(rec.get('year', ''))
            links.append('')
            if len(titles) >= max_total:
                break
        if len(titles) >= max_total:
            break

    # YouTube 서비스 초기화 및 플레이리스트 생성
    service = get_youtube_service(request.session)
    playlist_title = f"{e[0]} 추천 플레이리스트"
    playlist_id = create_playlist(
        service,
        title=playlist_title,
        description=f"{e[0]} 기반 자동 생성 리스트"
    )

    # 모든 곡을 YouTube 플레이리스트에 추가
    for link, title_, artist_ in zip(links, titles, artists):
        try:
            video_id = extract_video_id(link) or search_video(service, f"{title_} {artist_}")
            if video_id:
                safe_add_video(service, playlist_id, video_id)
        except Exception:
            # 실패한 아이템은 로그 처리 후 건너뜀
            continue

    playlist_url = f'https://www.youtube.com/playlist?list={playlist_id}'
    return titles, artists, albums, years, playlist_url