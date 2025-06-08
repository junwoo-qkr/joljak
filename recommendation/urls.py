from django.urls import path
from . import views

app_name = 'recommendation'

urlpatterns = [
    path('start/', views.start, name='start'),
    path('select_keywords/', views.select_keywords, name='sc'),
    path('result/', views.result, name='result'),
]