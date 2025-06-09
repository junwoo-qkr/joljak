from django.db import models

# Create your models here.
class music_list(models.Model):
    nation  = models.CharField(max_length=50)
    title   = models.CharField(max_length=200)
    artist  = models.CharField(max_length=200)
    album   = models.CharField(max_length=200)
    year    = models.IntegerField()
    y       = models.CharField(max_length=20)
    sector  = models.IntegerField()
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.artist}"