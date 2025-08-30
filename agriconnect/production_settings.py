"""
Production Settings for Agritrade Platform
Backend API: api.agritrade.cloud
Frontend App: app.agritrade.cloud
"""

import os
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='your-production-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Agritrade production domains
ALLOWED_HOSTS = [
    'api.agritrade.cloud',      # Backend API
    'app.agritrade.cloud',      # Frontend App
    'admin.agritrade.cloud',    # Admin Dashboard
    'staging.agritrade.cloud',  # Staging Environment
    'dev.agritrade.cloud',      # Development Environment
    'agritrade.cloud',          # Main domain
    'www.agritrade.cloud',      # WWW redirect
    'localhost',                # Local development
    '127.0.0.1'                # Local development
]

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
    'authentication',
    'payments',
    'orders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agriconnect.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'agriconnect.wsgi.application'

# Database - PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='agrictrading1_prod'),
        'USER': config('DB_USER', default='agrictrading1_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
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

# Internationalization for Ghana
LANGUAGE_CODE = 'en-gb'  # British English used in Ghana
TIME_ZONE = 'Africa/Accra'  # Ghana timezone
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

# Custom user model
AUTH_USER_MODEL = 'authentication.User'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# CORS settings for Agritrade production
CORS_ALLOWED_ORIGINS = [
    "https://app.agritrade.cloud",      # Frontend application
    "https://admin.agritrade.cloud",    # Admin dashboard
    "https://staging.agritrade.cloud",  # Staging environment
    "https://dev.agritrade.cloud",      # Development environment
    "https://agritrade.cloud",          # Main domain
    "https://www.agritrade.cloud",      # WWW domain
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.agritrade\.cloud$",  # Allow all agritrade.cloud subdomains
]

CORS_ALLOW_CREDENTIALS = True

# CSRF Configuration for Agritrade
CSRF_TRUSTED_ORIGINS = [
    "https://api.agritrade.cloud",
    "https://app.agritrade.cloud", 
    "https://admin.agritrade.cloud",
    "https://staging.agritrade.cloud",
    "https://dev.agritrade.cloud",
    "https://agritrade.cloud",
    "https://www.agritrade.cloud",
]

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Force HTTPS in production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Site URL for Ghana
SITE_URL = config('SITE_URL', default='https://agriconnect-ghana.herokuapp.com')

# Ghana-specific payment settings
DEFAULT_CURRENCY = config('DEFAULT_CURRENCY', default='GHS')
TARGET_MARKET = config('TARGET_MARKET', default='Ghana')

# Paystack settings for Ghana
PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY', default='')
PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY', default='')
PAYSTACK_WEBHOOK_SECRET = config('PAYSTACK_WEBHOOK_SECRET', default='')

# Email settings for Ghana (using Gmail SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = f'AgriConnect Ghana <{EMAIL_HOST_USER}>'

# Celery settings for background tasks
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Accra'

# Cache settings using Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Logging configuration for Ghana production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'agriconnect_ghana.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'payments': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'orders': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Ghana-specific business settings
GHANA_REGIONS = [
    'Greater Accra', 'Ashanti', 'Northern', 'Western', 'Eastern',
    'Central', 'Volta', 'Upper East', 'Upper West', 'Brong-Ahafo'
]

GHANA_MOBILE_OPERATORS = [
    {'name': 'MTN', 'ussd': '*170#', 'market_share': 70},
    {'name': 'Vodafone', 'ussd': '*110#', 'market_share': 20},
    {'name': 'AirtelTigo', 'ussd': '*185#', 'market_share': 10}
]

GHANA_AGRICULTURAL_SEASONS = {
    'major': {'period': 'April-July', 'crops': ['Maize', 'Rice', 'Yam']},
    'minor': {'period': 'September-December', 'crops': ['Maize', 'Cowpea']},
    'dry': {'period': 'November-March', 'crops': ['Tomato', 'Onion']}
}

# Payment limits for Ghana market (in GHS)
PAYMENT_LIMITS = {
    'minimum_amount': 1.00,
    'maximum_amount': 100000.00,
    'mobile_money_daily_limit': 5000.00,
    'bank_transfer_limit': 50000.00
}

# Feature flags for Ghana deployment
FEATURE_FLAGS = {
    'mobile_money_enabled': True,
    'cooperative_payments': True,
    'seasonal_pricing': True,
    'sms_notifications': True,
    'offline_payments': False,
    'multi_language': False
}
