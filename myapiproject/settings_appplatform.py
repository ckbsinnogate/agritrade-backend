"""
Simplified Production Settings for DigitalOcean App Platform
AgriTrade Django Backend - No File Logging Issues
"""
import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# Allowed hosts for production
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    ALLOWED_HOSTS = ['.ondigitalocean.app', 'localhost', '127.0.0.1', 'testserver', '*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
      # AgriTrade Applications (Core modules)
    'users',
    'products',
    'orders',
    'payments',
    'communications',
    'admin_dashboard',
    'advertisements',
    'ai',
    'farmer_dashboard',
    'financial',
    'processing',
    'reviews',
    'subscriptions',
    'traceability',
    'warehouses',
    'weather',    'authentication',
    'institution_dashboard',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myapiproject.urls'

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

WSGI_APPLICATION = 'myapiproject.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

# AI Service Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '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')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'anthropic/claude-3-haiku:beta')
OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '2048'))
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
OPENAI_TIMEOUT = int(os.getenv('OPENAI_TIMEOUT', '30'))

# AI Features Configuration
AI_FEATURES = {
    'CONVERSATIONAL_AI': True,
    'CROP_ADVISORY': True,
    'DISEASE_DETECTION': True,
    'MARKET_INTELLIGENCE': True,
    'MULTILINGUAL_SUPPORT': True,
    'SUPPORTED_LANGUAGES': ['en', 'tw', 'ha', 'yo'],
    'DEFAULT_LANGUAGE': 'en',
    'MAX_CONVERSATION_HISTORY': 10,
    'FEEDBACK_COLLECTION': True,
    'ANALYTICS_TRACKING': True,
}

# AI Usage Limits
AI_USAGE_LIMITS = {
    'DAILY_REQUESTS_PER_USER': 50,
    'MONTHLY_REQUESTS_PER_USER': 1000,
    'MAX_IMAGE_SIZE_MB': 10,
    'MAX_CONVERSATION_LENGTH': 20,
    'RATE_LIMIT_WINDOW': 60,
}

# Weather API Configuration
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS settings
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
if not CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGINS == ['']:
    CORS_ALLOWED_ORIGINS = [
        "https://agritrade-frontend.ondigitalocean.app",
    ]

CORS_ALLOW_CREDENTIALS = True

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

# Simple console-only logging (no file handlers)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{levelname}] {asctime} {name} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
