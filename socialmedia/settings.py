from pathlib import Path
import dj_database_url
import cloudinary
import cloudinary.api
import cloudinary.uploader

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dummy-key-for-now'   # ← replace me before going live
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    'rest_framework',
    'mediaapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'socialmedia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],   # <-- empty, we'll use app templates
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

WSGI_APPLICATION = 'socialmedia.wsgi.application'

DATABASES = {
    'default': dj_database_url.parse("postgresql://media_db_a1jp_user:Pi1YThDoseUQjZEMt7Bu6vLFhdMdPrlL@dpg-d8es43n7f7vs73dff5cg-a.oregon-postgres.render.com/media_db_a1jp")
}


# ---------- Static files (WhiteNoise) ----------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ---------- Cloudinary (hardcoded – safe for local dev) ----------
cloudinary.config(
    cloud_name="dqxemsd9j",
    api_key="579125639134454",
    api_secret="0w0p5CTR7R8WI_NvBJgwCrzqHjM",
    secure=True
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------- Authentication redirects ----------
LOGIN_REDIRECT_URL = 'feed'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'