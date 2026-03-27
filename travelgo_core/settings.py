"""
Django settings for travelgo_core project.
"""
from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load Local Environment Variables from .env file
load_dotenv()

# ─── Security ──────────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-unsafe-key-change-in-env!')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = allowed_hosts_env.split(',') if allowed_hosts_env != '*' else ['*']

# ─── API Keys ──────────────────────────────────────────────────────────────────

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')

# ─── Application Definition ────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',

    # Local Apps
    'users',
    'maps',
    'partners',
    'inventory',
    'quests',
]

AUTH_USER_MODEL = 'users.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'travelgo_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'travelgo_core.wsgi.application'

# ─── Database ──────────────────────────────────────────────────────────────────
# MVP: SQLite — PythonAnywhere Free Tier-ზე სრულიად ვარგა 500 მომხმარებლამდე.
# მომავალში: PostgreSQL + PostGIS (migrate-ით).
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── Password Validation ───────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Internationalization ──────────────────────────────────────────────────────

LANGUAGE_CODE = 'ka-ge'
TIME_ZONE = 'Asia/Tbilisi'
USE_I18N = True
USE_TZ = True

# ─── Static Files ──────────────────────────────────────────────────────────────

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── JWT Configuration ─────────────────────────────────────────────────────────

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
}

# ─── CORS ──────────────────────────────────────────────────────────────────────
# MVP: ყველა Origin-ს ვუშვებთ (Flutter local + production).
# Production-ში შეიზღუდება კონკრეტული დომენებით.
CORS_ALLOW_ALL_ORIGINS = True

# ─── Celery ────────────────────────────────────────────────────────────────────

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# ─── Cache (Redis) ─────────────────────────────────────────────────────────────

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}

# ─── Email ─────────────────────────────────────────────────────────────────────
# MVP: Console-ში ბეჭდავს მეილს (Redis PIN-ი მოქმედებს).
# Production-ში: EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'support@travelgo.ge'
