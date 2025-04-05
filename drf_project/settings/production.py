from .base import *
import sys
from decouple import config


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


