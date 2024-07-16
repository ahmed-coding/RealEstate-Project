from .base import *

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'daphne',
    'django_crontab',
    # "semantic_admin",
    # "semantic_forms",
    "admin_interface",
    "colorfield",
    # 'jet.dashboard',
    # 'jet',
    'import_export',
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
    'algoliasearch_django',
]

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.contrib.gis.db.backends.postgis',
    #     'USER': 'postgres',
    #     'NAME': 'test1',
    #     'HOST': 'localhost',
    #     'PORT': '5432',
    #     'PASSWORD': '12345',
    #     'TEST': {
    #         'NAME': 'mytestdatabase',
    #     },
    # },
    # 'default': {
    #     'ENGINE': 'django.contrib.gis.db.backends.postgis',
    #     'USER': 'postgres',
    #     'NAME': 'test3',
    #     'HOST': 'localhost',
    #     'PORT': '5432',
    #     'PASSWORD': '12345',
    #     'TEST': {
    #             'NAME': 'mytestdatabase',
    #     },
    # },
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'USER': 'postgres',
    #     'NAME': 'RealEstate',
    #     'HOST': 'postgres',
    #     'PORT': '5432',
    #     'PASSWORD': '12345',
    #     'TEST': {
    #         'NAME': 'mytestdatabase',
    #     },
    # },
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / '../db.sqlite3',
    }
}

CHANNEL_LAYERS = {
    # "default": {
    #     "BACKEND": "channels_redis.core.RedisChannelLayer",
    #     "CONFIG": {
    #         "hosts": [("redis", 6379)],
    #     },
    # },
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


# Media Files
