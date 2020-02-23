"""
Django settings for ksg_nett project.

Generated by 'django-admin startproject' using Django 1.10.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'rc4yscfoc9loe+937$q-57agxy0iq+!o0zowl0#vylilol2-)e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'channels',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',

    # Project apps
    'api',
    'common',
    'commissions',
    'economy',
    'external',
    'internal',
    'login',
    'organization',
    'quotes',
    'schedules',
    'summaries',
    'users',
    'chat'
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

ROOT_URLCONF = 'ksg_nett.urls'

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
    }
]

WSGI_APPLICATION = 'ksg_nett.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

# TODO: In case you didn't know, 6 characters is not enough nowadays...
# TODO: This should obviously be changed before production
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]
if not DEBUG:
    AUTH_PASSWORD_VALIDATORS += [
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

# Custom user
AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'ksg_nett.custom_authentication.UsernameOrEmailAuthenticationBackend'
]

# Default login_required return url
LOGIN_URL = '/'

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Override in production
LOCALE_PATHS = ['locales/', ]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Django REST framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAdminUser',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

STATIC_ROOT = 'static/'
MEDIA_ROOT = 'media/'

# Simple JWT SETTINGS
# ------------------------------
SIMPLE_JWT = {
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.SlidingToken',),
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=24),  # Should cover even the most hardcore Soci sessions
    'AUTH_HEADER_TYPES': ('JWT',),
}

# API DOCS
# ------------------------------
SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'api.api_docs.CustomSwaggerAutoSchema',
}

REDOC_SETTINGS = {
    'PATH_IN_MIDDLE': True,
    'REQUIRED_PROPS_FIRST': True
}

# ECONOMY SETTINGS
# ------------------------------
SOCI_MASTER_ACCOUNT_CARD_ID = 0xBADCAFEBABE  # Real card ids are 10 digits, while this is 14, meaning no collisions
DIRECT_CHARGE_SKU = "X-BELOP"

# Channels
ASGI_APPLICATION = 'ksg_nett.routing.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)]
        }
    }
}


# Redis
REDIS = {
    'host': 'localhost',
    'port': 6379
}
CHAT_STATE_REDIS_DB = 1


# Load local and production settings
try:
    from .settings_local import *
except ImportError:
    pass

if 'PROD' in os.environ:
    try:
        from .settings_prod import *
    except ImportError:
        pass
