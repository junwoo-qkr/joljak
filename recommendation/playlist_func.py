import random
from recommendation.models import music_list

def get_playlist(e, y, n):
    emotion_dict = {'Delighted': 0,
                    'Happy': 1,
                    'Anxious': 2,
                    'Angry': 3,
                    'Depressed': 4,
                    'Tired': 5,
                    'Calm': 6,
                    'Satisfied': 7
                    }
    emo_code = emotion_dict[e[0]]

    qs = music_list.objects.filter(
        nation__in = n,
        y__in = y,
        sector = emo_code,
    )
    
    count = qs.count()
    if count == 0:
        return [], [], [], [], []
    
    ids = list(qs.values_list('id', flat=True))
    sample_ids = random.sample(ids, min(5, count))
    samples = music_list.objects.filter(id__in=sample_ids)

    titles = [m.title for m in samples]
    artists = [m.artist for m in samples]
    albums = [m.album for m in samples]
    years = [m.year for m in samples]
    links = [m.link for m in samples]

    return titles, artists, albums, years, links