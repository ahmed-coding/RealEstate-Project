from .base import *
ALLOWED_HOSTS = ['*']


DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'USER': 'fashion_0ht9_user',
    #     'NAME': 'fashion_0ht9',
    #     'HOST': 'dpg-cmgte5f109ks7399c8lg-a.oregon-postgres.render.com',
    #     'PORT': '5432',
    #     'PASSWORD': 'mzEeC0xbG6yg6rDiIyTzokI1dB9DGgt6',
    #     'TEST': {
    #         'NAME': 'mytestdatabase',
    #     },
    # }
    # },
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'USER': 'postgres',
    #     'NAME': 'QAEnvironment',
    #     'HOST': 'localhost',
    #     'PORT': '3306',
    #     'PASSWORD': '',
    #     'TEST': {
    #         'NAME': 'mytestdatabase',
    #     },
    # },
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / '../db.sqlite3',
    }
}

# Media Files

CHANNEL_LAYERS = {
    # "default": {
    #     "BACKEND": "channels_redis.core.RedisChannelLayer",
    #     "CONFIG": {
    #         "hosts": [("localhost", 6379)],
    #     },
    # },
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
