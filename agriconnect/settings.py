"""
AgriConnect API - Africa's Premier Agricultural Commerce Platform
Settings Configuration for Pan-African Agricultural Trade

Based on comprehensive PRD with dual authentication, blockchain traceability,
escrow payments, warehouse management, and SMS integration.
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Configuration
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver').split(',')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.gis',  # Disabled for now due to PostgreSQL version requirements
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_extensions',
    'django_filters',
]

LOCAL_APPS = [
    'authentication',
    'users',  # User profiles and enhanced user management
    'products',
    'warehouses',
    'orders',
    'payments',
    'financial',  # Financial services - loan management and investment tracking
    'traceability',
    'reviews',
    'subscriptions',
    'communications',
    'advertisements',
    'processing',  # Processing management system
    'processors',  # Recipe sharing and processor integration
    'ai',  # AI-powered agricultural intelligence
    'weather',  # Weather services and current weather API
    'contracts',  # Contract management for institutions
    'analytics',  # Analytics and dashboard data
    'institution_dashboard',  # Institution Dashboard protection system
    'admin_dashboard',  # Administrator Dashboard Platform Overview & Management
    'farmer_dashboard',  # Farmer Dashboard comprehensive management system
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware Configuration
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'admin_dashboard.middleware.AdminDashboardProtectionMiddleware',  # Admin dashboard protection FIRST
    'admin_dashboard.middleware.AdminDashboardLoggingMiddleware',  # Admin dashboard logging SECOND
    'institution_dashboard.middleware.InstitutionDashboardProtectionMiddleware',  # Rate limiting and circuit breaker
    'institution_dashboard.middleware.InstitutionDashboardLoggingMiddleware',  # Enhanced logging  
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
        'DIRS': [BASE_DIR / 'templates'],
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

# Database Configuration - PostgreSQL
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='postgresql://postgres:kingsco45@localhost:5432/agriconnect_db'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Use regular PostgreSQL backend (not PostGIS) due to version requirements
DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'

# GDAL/GEOS Configuration for Geographic Support
GDAL_LIBRARY_PATH = config('GDAL_LIBRARY_PATH', default=r"C:\OSGeo4W\bin\gdal310.dll")
GEOS_LIBRARY_PATH = config('GEOS_LIBRARY_PATH', default=r"C:\OSGeo4W\bin\geos_c.dll")


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization - Pan-African Language Support
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Africa/Accra'  # Ghana timezone as AfCFTA headquarters
USE_I18N = True
USE_TZ = True

# Supported Languages (from PRD)
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'French'),
    ('tw', 'Twi'),
    ('ee', 'Ewe'),
    ('ha', 'Hausa'),
    ('yo', 'Yoruba'),
    ('sw', 'Swahili'),
    ('ar', 'Arabic'),
]

# Static and Media Files
STATIC_URL = '/static/'
STATIC_ROOT = config('STATIC_ROOT', default=BASE_DIR / 'staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = config('MEDIA_ROOT', default=BASE_DIR / 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model (Dual Authentication)
AUTH_USER_MODEL = 'authentication.User'

# GDAL/GEOS Configuration for Geographic Data Support
GDAL_LIBRARY_PATH = config('GDAL_LIBRARY_PATH', default=r"C:\OSGeo4W\bin\gdal310.dll")
GEOS_LIBRARY_PATH = config('GEOS_LIBRARY_PATH', default=r"C:\OSGeo4W\bin\geos_c.dll")

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',  # Re-enabled for advanced filtering
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'otp': '3/10min',
        'registration': '5/hour',
        # SMS OTP specific rate limits
        'sms_otp_phone': '5/hour',     # Max 5 SMS OTP per hour per phone number
        'sms_otp_ip': '10/hour',       # Max 10 SMS OTP per hour per IP address
        'sms_otp_verify': '10/minute', # Max 10 verification attempts per minute
        # Institution Dashboard specific rate limits to prevent infinite loops
        'institution_dashboard_anon': '10/minute',  # Max 10 unauthenticated requests per minute
        'institution_dashboard_user': '300/hour',   # Max 300 authenticated requests per hour
        # Admin Dashboard specific rate limits (more generous for admin operations)
        'admin_dashboard_anon': '50/minute',  # Max 50 unauthenticated requests per minute
        'admin_dashboard_user': '500/hour',   # Max 500 authenticated requests per hour for regular users
        'admin_exempt': 'none',  # No limits for authenticated admin users
        # Analytics specific rate limits (higher for data-heavy operations)
        'analytics': '200/hour',  # Max 200 analytics requests per hour for regular users
        'analytics_admin': '1000/hour',  # Max 1000 analytics requests per hour for admin users
    }
}

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'AgriConnect',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', 
    default='http://localhost:3000,http://127.0.0.1:3000'
).split(',')

CORS_ALLOW_CREDENTIALS = True

# Cache Configuration (Using Django's default cache for development)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# SMS OTP Configuration for Professional Authentication
SMS_OTP_SETTINGS = {
    # Core settings
    'OTP_LENGTH': 6,
    'OTP_EXPIRY_MINUTES': 10,
    'MAX_ATTEMPTS': 3,
    'RESEND_COOLDOWN_SECONDS': 60,
    
    # Rate limiting
    'RATE_LIMIT_PHONE_PER_HOUR': 5,
    'RATE_LIMIT_IP_PER_HOUR': 10,
    'RATE_LIMIT_GLOBAL_PER_MINUTE': 20,
    
    # SMS provider settings (AVRSMS)
    'PROVIDER': 'avrsms',
    'SENDER_ID': 'AgriConnect',
    'SMS_TIMEOUT': 30,
    
    # Phone number settings
    'DEFAULT_COUNTRY_CODE': '+233',  # Ghana
    'SUPPORTED_COUNTRIES': {
        'ghana': '+233',
        'nigeria': '+234',
        'kenya': '+254',
        'south_africa': '+27',
        'senegal': '+221',
        'tanzania': '+255',
        'uganda': '+256',
        'zambia': '+260',
        'ivory_coast': '+225',
        'mali': '+223'
    },
    
    # Security settings
    'REQUIRE_PHONE_VERIFICATION': True,
    'AUTO_VERIFY_USER_ON_SUCCESS': True,
    'GENERATE_JWT_ON_VERIFICATION': True,
    
    # Template settings
    'SMS_TEMPLATE_CONTEXT': {
        'company_name': 'AgriConnect',
        'support_phone': '+233200000000',
        'app_name': 'AgriConnect',
        'brand_name': 'AgriConnect'
    },
    
    # Cleanup settings
    'AUTO_CLEANUP_EXPIRED_OTPS': True,
    'CLEANUP_AFTER_DAYS': 7,
    
    # Logging
    'LOG_SMS_SENDS': True,
    'LOG_VERIFICATION_ATTEMPTS': True,
    'LOG_RATE_LIMIT_HITS': True,
}

# SMS Configuration
SMS_CONFIG = {
    'API_KEY': config('SMS_API_KEY', default=''),
    'API_SECRET': config('SMS_API_SECRET', default=''),
    'SENDER_ID': config('SMS_SENDER_ID', default='AgriConnect'),
    'PROVIDERS': {
        'hubtel': {
            'url': 'https://smsc.hubtel.com/v1/messages/send',
            'priority': 1,
        },
        'africas_talking': {
            'url': 'https://api.africastalking.com/version1/messaging',
            'priority': 2,
        },
        'twilio': {
            'url': 'https://api.twilio.com/2010-04-01/Accounts',
            'priority': 3,
        }
    }
}

# SMS/USSD Configuration for Farmer Onboarding
SMS_CONFIG = {
    'ENABLED': True,
    'PROVIDER': 'avrsms',  # Using AVRSMS as the SMS provider
    'SANDBOX_MODE': False,  # Set to True for testing
    'SUPPORTED_COUNTRIES': {
        'ghana': '+233',
        'nigeria': '+234', 
        'kenya': '+254',
        'south_africa': '+27',
        'senegal': '+221',
        'tanzania': '+255',
        'uganda': '+256',
        'zambia': '+260',
        'ivory_coast': '+225',
        'mali': '+223'
    },
    'USSD_CODE': '*123#',
    'SHORT_CODE': '40404',
    'SENDER_ID': 'AgriConnect'
}

# AVRSMS API Configuration
AVRSMS_API_ID = 'API113898428691'
AVRSMS_API_PASSWORD = 'Kingsco45@1'
AVRSMS_BASE_URL = 'https://api.avrsms.com'  # Updated to match API docs
AVRSMS_SENDER_ID = 'AgriConnect'  # Your registered sender ID
AVRSMS_SMS_TYPE = 'P'  # P for Promotional, T for Transactional (account limited to promotional)
AVRSMS_ENCODING = 'T'  # T for Text, U for Unicode

# SMS Language Configuration
SMS_LANGUAGES = {
    'en': 'English',
    'tw': 'Twi',
    'ha': 'Hausa',
    'yo': 'Yoruba',
    'ig': 'Igbo',
    'fr': 'French',
    'sw': 'Swahili',
    'am': 'Amharic'
}

# SMS Rate Limiting
SMS_RATE_LIMITS = {
    'SMS_PER_MINUTE': 10,
    'SMS_PER_HOUR': 100,
    'SMS_PER_DAY': 500,
    'USSD_SESSIONS_PER_HOUR': 50
}

# Payment Gateway Configuration
PAYMENT_CONFIG = {
    'PAYSTACK': {
        'SECRET_KEY': config('PAYSTACK_SECRET_KEY', default=''),
        'PUBLIC_KEY': config('PAYSTACK_PUBLIC_KEY', default=''),
    },
    'FLUTTERWAVE': {
        'SECRET_KEY': config('FLUTTERWAVE_SECRET_KEY', default=''),
        'PUBLIC_KEY': config('FLUTTERWAVE_PUBLIC_KEY', default=''),
    }
}

# Blockchain Configuration
BLOCKCHAIN_CONFIG = {
    'POLYGON_RPC_URL': config('POLYGON_RPC_URL', default=''),
    'ETHEREUM_RPC_URL': config('ETHEREUM_RPC_URL', default=''),
    'IPFS_GATEWAY': 'https://ipfs.io/ipfs/',
}

# Email Configuration - Mailtrap for Development and Production Testing
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='sandbox.smtp.mailtrap.io')
EMAIL_PORT = config('EMAIL_PORT', default=2525, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='5a06a8a300b393')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='61353f9d61027c')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='AgriConnect <noreply@agriconnect.com>')

# Email OTP Configuration - Professional OTP Settings with 40+ years experience
EMAIL_OTP_SETTINGS = {
    'OTP_LENGTH': 6,                    # Standard 6-digit OTP
    'OTP_EXPIRY_MINUTES': 10,           # 10 minutes expiry for security
    'MAX_ATTEMPTS': 3,                  # Maximum verification attempts
    'RESEND_COOLDOWN_SECONDS': 60,      # 1 minute cooldown between sends
    'MAX_DAILY_SENDS': 10,              # Daily send limit per email
    'RATE_LIMIT_WINDOW_HOURS': 24,      # Rate limiting window
    'OTP_CHARSET': 'numeric',           # Use only numbers for better UX
    'SEND_HTML': True,                  # Send HTML formatted emails
    'COMPANY_NAME': 'AgriConnect',
    'COMPANY_SUPPORT_EMAIL': 'support@agriconnect.com',
    'BRAND_COLOR': '#2E7D4F',          # AgriConnect green
    'TEMPLATE_CONTEXT': {
        'company_name': 'AgriConnect',
        'company_url': 'https://agriconnect.com',
        'support_email': 'support@agriconnect.com',
        'app_name': 'AgriConnect - Africa\'s Premier Agricultural Commerce Platform'
    }
}

# Celery Configuration (Background Tasks)
CELERY_BROKER_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://127.0.0.1:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'institution_dashboard': {
            'format': '[INSTITUTION-DASHBOARD] {levelname} {asctime} {name} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'agriconnect.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'institution_dashboard_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'institution_dashboard.log',
            'formatter': 'institution_dashboard',
        },
        'institution_dashboard_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'institution_dashboard',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'agriconnect': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'institution_dashboard': {
            'handlers': ['institution_dashboard_console', 'institution_dashboard_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'analytics': {
            'handlers': ['console', 'file', 'institution_dashboard_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# OpenAI/OpenRouter AI Configuration
OPENAI_API_KEY = config('OPENAI_API_KEY', default='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')
OPENAI_BASE_URL = config('OPENAI_BASE_URL', default='https://openrouter.ai/api/v1')
OPENAI_MODEL = config('OPENAI_MODEL', default='anthropic/claude-3-haiku:beta')
OPENAI_MAX_TOKENS = config('OPENAI_MAX_TOKENS', default=2048, cast=int)
OPENAI_TEMPERATURE = config('OPENAI_TEMPERATURE', default=0.7, cast=float)
OPENAI_TIMEOUT = config('OPENAI_TIMEOUT', default=30, cast=int)

# AI Features Configuration
AI_FEATURES = {
    'CONVERSATIONAL_AI': True,
    'CROP_ADVISORY': True,
    'DISEASE_DETECTION': True,
    'MARKET_INTELLIGENCE': True,
    'MULTILINGUAL_SUPPORT': True,
    'SUPPORTED_LANGUAGES': ['en', 'tw', 'ha', 'yo'],  # English, Twi, Hausa, Yoruba
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
    'RATE_LIMIT_WINDOW': 60,  # seconds
}
