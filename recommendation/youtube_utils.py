import re
from django.conf import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_youtube_service(session):
    data = session.get('youtube_credentials')
    creds = Credentials(**data)
    return build('youtube', 'v3', credentials=creds)

def create_playlist(service, title, description):
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
    return res['id']

def extract_video_id(url):
    m = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})', url)
    return m.group(1) if m else None

def search_video(service, query):
    req = service.search().list(
        part='id',
        q=query,
        type='video',
        maxResults=1
    ).execute()
    items = req.get('items', [])
    return items[0]['id']['videoId'] if items else None

def add_video_to_playlist(service, playlist_id, video_id):
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