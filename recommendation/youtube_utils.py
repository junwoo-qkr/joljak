import re
from django.conf import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_youtube_service(session):
    # 세션에 저장된 직렬화된 credentials 로 복원
    data = session.get('youtube_credentials')
    creds = Credentials(**data)
    return build('youtube', 'v3', credentials=creds)

def create_playlist(service, title, description):
    # playlists.insert 메서드로 신규 플레이리스트 생성
    res = service.playlists().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': title,
                'description': description
            },
            'status': {
                'privacyStatus': 'public'
            }
        }
    ).execute()
    return res['id']  # 새로 생성된 플레이리스트 ID 반환 :contentReference[oaicite:3]{index=3}

def extract_video_id(url):
    # URL에서 videoId 부분만 꺼내기
    m = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})', url)
    return m.group(1) if m else None

def search_video(service, query):
    # 제목·아티스트 키워드로 동영상 검색
    req = service.search().list(
        part='id',
        q=query,
        type='video',
        maxResults=1
    ).execute()
    items = req.get('items', [])
    return items[0]['id']['videoId'] if items else None

def add_video_to_playlist(service, playlist_id, video_id):
    # playlistItems.insert 로 플레이리스트에 영상 추가
    service.playlistItems().insert(
        part='snippet',
        body={
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }
    ).execute()