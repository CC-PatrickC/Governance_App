"""
Django settings for project_intake project - SQLite version for local testing
"""
from .settings import *

# Override database to use SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Also allow local testing without SSL
SECURE_PROXY_SSL_HEADER = None