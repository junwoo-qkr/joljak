from django.shortcuts import render, redirect
from django.http import JsonResponse
from .playlist_func import get_playlist

# Create your views here.
def start(request):
    return render(request, 'main.html')

def select_keywords(request):
    return render(request, 'recommendation.html')

def result(request):
    EMOTIONS = request.POST.getlist('emotions')
    YEARS = request.POST.getlist('years')
    NATION = request.POST.getlist('nation')
    # print(EMOTIONS, YEARS, NATION)
    title, artist, album, year, link = get_playlist(EMOTIONS, YEARS, NATION)
    songs = list(zip(title, artist, album, year))
    print(title, artist, album, year)
    return render(request, 'result.html',
                  {'e': EMOTIONS, 'y': YEARS, 'n': NATION, 'songs': songs})