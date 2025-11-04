from django.urls import path
from . import views

app_name = 'recommendation'

urlpatterns = [
    path('start/', views.start, name='start'),
    path('select_keywords/', views.select_keywords, name='sc'),
    path('about/', views.about, name='about'),
    path('history/', views.playlist_history, name='history'),
    path('result/', views.result, name='result'),
    path('error/', views.error_page, name='error_page'),
    path('youtube/authorize/', views.youtube_authorize, name='youtube_authorize'),
    path('oauth2callback/', views.youtube_oauth2callback, name='youtube_oauth2callback'),
    path('contact/', views.contact, name='contact'),
]