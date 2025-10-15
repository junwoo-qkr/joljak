from django.shortcuts import render, redirect
from .playlist_func import get_playlist
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from google.auth.exceptions import RefreshError
from django.core.cache import cache

# for revoke test
import requests
from django.http import HttpResponse

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


def playlist_history(request):
    history = cache.get('playlist-history-cache', []).reverse()
    return render(request, 'history.html', {'playlist': history})


def select_keywords(request):
    return render(request, 'recommendation.html')


def about(request):
    return render(request, 'about.html')


def result(request):
    if request.method == 'POST':
        request.session['form_data'] = {
            'emotions': request.POST.getlist('emotions'),
            'years': request.POST.getlist('years')
        }
        return redirect('recommendation:result')
    
    if not request.session.get('youtube_credentials'):
        return redirect('recommendation:youtube_authorize')
    
    EMOTIONS = request.session.get('form_data')['emotions']
    YEARS = request.session.get('form_data')['years']
    
    try:
        # YouTube API를 호출하는 함수를 try 블록으로 감쌉니다.
        title, artist, album, year, link = get_playlist(request, EMOTIONS, YEARS)
        songs = list(zip(title, artist, album, year))
        
        return render(
            request, 
            'result.html',
            {'e': EMOTIONS, 'y': YEARS, 'songs': songs, 'link': link}
        )

    except RefreshError:
        # RefreshError가 발생하면(토큰 만료/무효), 세션 정보를 삭제하고 다시 인증 페이지로 리디렉션합니다.
        if 'youtube_credentials' in request.session:
            del request.session['youtube_credentials']
        
        return redirect('recommendation:youtube_authorize')
    
# for revoke test
'''
def revoke_token(request):
    """세션에 저장된 구글 리프레시 토큰을 강제로 해지하는 테스트용 뷰"""
    credentials = request.session.get('youtube_credentials')
    if not credentials or 'refresh_token' not in credentials:
        return HttpResponse("세션에 유효한 인증 정보가 없습니다. 먼저 인증을 받아주세요.")

    refresh_token = credentials['refresh_token']

    # Google의 토큰 해지 엔드포인트에 요청 전송
    response = requests.post('https://oauth2.googleapis.com/revoke',
        params={'token': refresh_token},
        headers={'content-type': 'application/x-www-form-urlencoded'})

    if response.status_code == 200:
        # 성공적으로 해지되면 세션의 인증 정보도 삭제
        if 'youtube_credentials' in request.session:
            del request.session['youtube_credentials']
        return HttpResponse("토큰이 성공적으로 해지(revoke)되었습니다. 이제 result 페이지로 가서 테스트하세요.")
    else:
        return HttpResponse(f"토큰 해지 실패: {response.text}", status=response.status_code)
'''