import time
from django.conf import settings
from googleapiclient.errors import HttpError
from recommendation.models import music_list
from django.core.cache import cache
from .youtube_utils import (
    get_youtube_service, create_playlist,
    extract_video_id, search_video, add_video_to_playlist
)


def safe_add_video(service, playlist_id, video_id, retries=3, delay=2):
    for attempt in range(retries):
        try:
            add_video_to_playlist(service, playlist_id, video_id)
            return True
        except HttpError as e:
            status = e.resp.status
            if status in (409, 503):
                time.sleep(delay * (2 ** attempt))
                continue
            raise
    return False


def get_playlist(request, e, y):
    emotion_dict = {
        'Delighted': 0, 'Happy': 1, 'Anxious': 2,
        'Angry': 3, 'Depressed': 4, 'Tired': 5,
        'Calm': 6, 'Satisfied': 7, 'Unknown': 8
    }
    emo_code = emotion_dict.get(e[0])
    qs = music_list.objects.filter(y__in=y, sector=emo_code)

    if not qs.exists():
        return [], [], [], [], ''

    sample_qs = qs.order_by('?')[:20]
    titles = [m.title for m in sample_qs]
    artists = [m.artist for m in sample_qs]
    albums = [m.album for m in sample_qs]
    years = [m.year for m in sample_qs]
    links = [m.link for m in sample_qs]

    service = get_youtube_service(request.session)
    playlist_title = f"{e[0]} 추천 플레이리스트"
    playlist_id = create_playlist(
        service,
        title=playlist_title,
        description=f"{e[0]} 기반 자동 생성 리스트"
    )
    playlist_url = f'https://www.youtube.com/playlist?list={playlist_id}'

    for link, title_, artist_ in zip(links, titles, artists):
        try:
            video_id = extract_video_id(link) or search_video(service, f"{title_} {artist_}")
            if video_id:
                safe_add_video(service, playlist_id, video_id)
        except Exception:
            continue

    playlist_history = cache.get('playlist-history-cache', [])
    if len(playlist_history) >= 5:
        playlist_history.pop(0)

    playlist_history.append(
        {
            'title': playlist_title,
            'url': playlist_url,
            'songs': list(zip(titles, artists, albums, years))
        }
    )
    cache.set('playlist-history-cache', playlist_history, timeout=None)
    
    return titles, artists, albums, years, playlist_url