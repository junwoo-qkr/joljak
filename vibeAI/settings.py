from pathlib import Path
import environ
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)

environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('DJANGO_SECRET_KEY')
GOOGLE_WEB_CONFIG = {
    "web": {
        "client_id": env('GOOGLE_CLIENT_ID'),
        "project_id": env('GOOGLE_PROJECT_ID'),
        "auth_uri": env('GOOGLE_AUTH_URI'),
        "token_uri": env('GOOGLE_TOKEN_URI'),
        "auth_provider_x509_cert_url": env('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
        "client_secret": env('GOOGLE_CLIENT_SECRET'),
        "redirect_uris": env('GOOGLE_REDIRECT_URIS').split(','),
        "javascript_origins": env('GOOGLE_JAVASCRIPT_ORIGINS').split(',')
    }
}

DEBUG = True if env('DEBUG') == 'True' else False

YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube']

if DEBUG == True:
    YOUTUBE_OAUTH2_CALLBACK = 'http://127.0.0.1:8000/recommendation/oauth2callback/' # 로컬용
    ALLOWED_HOSTS = []

elif DEBUG == False:
    YOUTUBE_OAUTH2_CALLBACK = 'https://qkrjunwoo.pythonanywhere.com/recommendation/oauth2callback/' # 배포용
    ALLOWED_HOSTS = ['qkrjunwoo.pythonanywhere.com']

INSTALLED_APPS = [
    'recommendation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vibeAI.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'vibeAI.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'assets'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CAHCHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'playlist-history-cache',
    }
}