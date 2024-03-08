"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-%m2=vfc6yd@^m_qmg1@bubht_kg!8j)g!g_8^ex1*za+=u@si)'

# DEBUG = os.environ.get('DEBUG')
DEBUG = True

AUTH_USER_MODEL = 'apps.User'

DEFAULT_CHARSET = 'utf-8'


INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # internl apps
    'apps',
    # # external apps
    'mptt',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'user_agents',
    'drf_spectacular',
    'schema_graph',
    'corsheaders',
    'channels',
    'channels_redis',

]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware'  # ,
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / '../apps/templates'],
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

WSGI_APPLICATION = "core.wsgi.application"

ASGI_APPLICATION = "core.asgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/


STATIC_URL = 'static/'

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "../static",

]
STATIC_ROOT = BASE_DIR / '../assets'


APPEND_SLASH = True

# AUTHENTICATION_BACKENDS = (
#     'django.contrib.auth.backends.AllowAllUsersModelBackend',
#     'apps.backends.CaseInsensitiveModelBackend',
# )


# Rest_framework
REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',


    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']

    # 'DEFAULT_RENDERER_CLASSES': [
    #     'rest_framework.renderers.JSONRenderer',
    # ],
    # 'DEFAULT_PARSER_CLASSES': [
    #     'rest_framework.parsers.JSONParser',
    # ],
    # 'DEFAULT_CONTENT_NEGOTIATION_CLASS':
    #     'rest_framework.negotiation.DefaultContentNegotiation',

}

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SPECTACULAR Swagger documentation settings
SPECTACULAR_SETTINGS = {
    'TITLE': ' API Documentation for RealEstate ',
    'DESCRIPTION': 'RealEstate project description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,
    # OTHER SETTINGS
}

# LOGIN_REDIRECT_URL = '/'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


MEDIA_URL = 'media/'
MEDIAFILES_DIRS = [
    BASE_DIR / "../media",
]
MEDIA_ROOT = BASE_DIR / '../media'

CORS_ORIGIN_ALLOW_ALL = True  # -> Cors Header

# CORS_ORIGIN_WHITELIST = (
#     'http://localhost:8000',
#     'http://192.168.1.100:8080',
# )

# Channels settings