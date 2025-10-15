from django.contrib import admin
from django.db import models
from .models import music_list

@admin.register(music_list)
class MusicListAdmin(admin.ModelAdmin):
    list_display = [field.name for field in music_list._meta.fields]

    search_fields = [
        field.name
        for field in music_list._meta.fields
        if isinstance(field, (models.CharField, models.TextField))
    ]

    list_filter = [
        field.name
        for field in music_list._meta.fields
        if isinstance(field, (models.BooleanField, models.DateField, models.ForeignKey))
    ]