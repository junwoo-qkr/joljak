from django.shortcuts import render, redirect
from django.http import JsonResponse
from .playlist_func import get_playlist
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# Create your views here.
def youtube_authorize(request):
    flow = Flow.from_client_secrets_file(
        settings.YOUTUBE_CLIENT_SECRETS_FILE,
        scopes=settings.YOUTUBE_SCOPES,
        redirect_uri=settings.YOUTUBE_OAUTH2_CALLBACK
    )
    auth_url, state = flow.authorization_url(
        access_type='offline',           # refresh token 획득
        include_granted_scopes='true',    # 이미 승인된 범위도 포함
        prompt='consent'                  # 동의 화면을 매번 띄우기
    )
    request.session['oauth_state'] = state
    return redirect(auth_url)

def youtube_oauth2callback(request):
    state = request.session.pop('oauth_state', None)
    flow = Flow.from_client_secrets_file(
        settings.YOUTUBE_CLIENT_SECRETS_FILE,
        scopes=settings.YOUTUBE_SCOPES,
        redirect_uri=settings.YOUTUBE_OAUTH2_CALLBACK,
        state=state
    )
    # Google로부터 받은 코드로 토큰 교환
    flow.fetch_token(code=request.GET.get('code'))
    creds = flow.credentials

    # 세션(또는 데이터베이스)에 직렬화하여 저장
    request.session['youtube_credentials'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri':   creds.token_uri,
        'client_id':   creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes,
    }
    return redirect('recommendation:result')



def start(request):
    return render(request, 'main.html')

def select_keywords(request):
    return render(request, 'recommendation.html')

def result(request):
    if not request.session.get('youtube_credentials'):
        return redirect('recommendation:youtube_authorize')
    
    EMOTIONS = request.POST.getlist('emotions')
    YEARS = request.POST.getlist('years')
    NATION = request.POST.getlist('nation')
    # print(EMOTIONS, YEARS, NATION)
    
    title, artist, album, year, link = get_playlist(request, EMOTIONS, YEARS, NATION)
    songs = list(zip(title, artist, album, year))
    print(title, artist, album, year)
    
    return render(request, 'result.html',
                  {'e': EMOTIONS, 'y': YEARS, 'n': NATION, 'songs': songs, 'link': link})