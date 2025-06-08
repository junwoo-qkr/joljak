import numpy as np
import pandas as pd
import os

def get_playlist(e, y, n):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, 'music_list.xlsx')
    df = pd.read_excel(excel_path)
    df = df[['nation', 'title', 'artist', 'album', 'year', 'y', 'sector']]
    # df['sector'] = df['sector'].astype(int)

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
    mask = df['nation'].isin(n) & df['y'].isin(y) & (df['sector'] == emo_code)
    dst = df.loc[mask]
    dst = dst.sample(n=min(5, len(dst)), random_state=None)
    
    print(emo_code, e, y, n)
    print(dst.head())

    return(dst['title'].tolist(), dst['artist'].tolist(), dst['album'].tolist(), dst['year'].tolist())