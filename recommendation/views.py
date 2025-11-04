from django.shortcuts import render, redirect
from .playlist_func import get_playlist
from django.conf import settings
from google_auth_oauthlib.flow import Flow
from google.auth.exceptions import RefreshError
from django.core.cache import cache

def youtube_authorize(request):
    flow = Flow.from_client_config(
        settings.GOOGLE_WEB_CONFIG,
        scopes=settings.YOUTUBE_SCOPES
    )
    flow.redirect_uri = settings.YOUTUBE_OAUTH2_CALLBACK

    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    request.session['oauth_state'] = state
    return redirect(auth_url)


def youtube_oauth2callback(request):
    state = request.session.pop('oauth_state', None)
    flow = Flow.from_client_config(
        settings.GOOGLE_WEB_CONFIG,
        scopes=settings.YOUTUBE_SCOPES,
        state=state
    )
    flow.redirect_uri = settings.YOUTUBE_OAUTH2_CALLBACK

    flow.fetch_token(code=request.GET.get('code'))
    creds = flow.credentials

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
    history = cache.get('playlist-history-cache', [])
    history = list(reversed(history))
    return render(request, 'history.html', {'playlist_history': history})


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
        title, artist, album, year, link = get_playlist(request, EMOTIONS, YEARS)
        songs = list(zip(title, artist, album, year))
        
        return render(
            request, 
            'result.html',
            {'e': EMOTIONS, 'y': YEARS, 'songs': songs, 'link': link}
        )

    except RefreshError:
        if 'youtube_credentials' in request.session:
            del request.session['youtube_credentials']
        return redirect('recommendation:youtube_authorize')

    except Exception as e:
        request.session['error_message'] = str(e)
        return redirect('recommendation:error_page')


def error_page(request):
    error_message = request.session.pop('error_message', None)
    if not error_message:
        error_message = '에러가 일어나지 않았어요! 왜 온거죠?'
    return render(request, 'error.html', {'error_message': error_message})


def contact(request):
    return render(request, 'contact.html')