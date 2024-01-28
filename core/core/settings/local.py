from .base import *

ALLOWED_HOSTS = ['*']

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
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'postgres',
        'NAME': 'RealEstate',
        'HOST': 'postgres',
        'PORT': '5432',
        'PASSWORD': '12345',
        'TEST': {
            'NAME': 'mytestdatabase',
        },
    },
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / '../db.sqlite3',
    # }
}


# Media Files
