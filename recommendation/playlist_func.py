import random
from recommendation.models import music_list
from .youtube_utils import (
    get_youtube_service, create_playlist,
    extract_video_id, search_video, add_video_to_playlist
)

def get_playlist(request, e, y, n):
    emotion_dict = {
        'Delighted': 0,
        'Happy': 1,
        'Anxious': 2,
        'Angry': 3,
        'Depressed': 4,
        'Tired': 5,
        'Calm': 6,
        'Satisfied': 7
    }
    emo_code = emotion_dict[e[0]]

    qs = music_list.objects.filter(
        nation__in = n,
        y__in = y,
        sector = emo_code,
    )
    
    count = qs.count()
    if count == 0:
        return [], [], [], [], []
    
    ids = list(qs.values_list('id', flat=True))
    sample_ids = random.sample(ids, min(5, count))
    samples = music_list.objects.filter(id__in=sample_ids)

    titles = [m.title for m in samples]
    artists = [m.artist for m in samples]
    albums = [m.album for m in samples]
    years = [m.year for m in samples]
    links = [m.link for m in samples]

    service = get_youtube_service(request.session)

    playlist_id = create_playlist(
        service,
        title       = 'playlist',
        description = 'recommended playlist'
    )

    for link, title, artist in zip(links, titles, artists):
        video_id = extract_video_id(link) or search_video(service, f'{title} {artist}')
        if video_id:
            add_video_to_playlist(service, playlist_id, video_id)
        # 검색 실패 시 로깅하거나 생략 가능

    # 5) 최종 URL 생성
    playlist_url = f'https://www.youtube.com/playlist?list={playlist_id}'

    # 6) 기존 반환값 5개 리스트 + 플레이리스트 URL
    return titles, artists, albums, years, playlist_url