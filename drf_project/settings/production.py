from .base import *
import sys
from decouple import config
import dj_database_url

DEBUG = False

ALLOWED_HOSTS =['https://viva-estate-backend.onrender.com']
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}


DATABASES = {
    'default': dj_database_url.config(
        default=config("DATABASE_URL")  # Uses the Render database URL
    )
}