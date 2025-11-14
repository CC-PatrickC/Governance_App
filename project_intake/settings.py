"""
Django settings for project_intake project - CLEAN VERSION FOR DEPLOYMENT
"""
from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

ENABLE_CAS = os.getenv("DJANGO_ENABLE_CAS", "false").lower() in ("1", "true", "yes")
ENABLE_AZURE_AD = os.getenv("DJANGO_ENABLE_AZURE_AD", "false").lower() in ("1", "true", "yes")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-please-change")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() in ("1", "true", "yes")

# Hosts & proxy configuration
DEFAULT_HOSTS = "localhost,127.0.0.1,govapp-fbhde3c8ffg9fbf9.westus2-01.azurewebsites.net,governance.coloradocollege.app"
ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", DEFAULT_HOSTS).split(",") if host.strip()]

CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS if host not in ("localhost", "127.0.0.1")]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'projects',
    'crispy_forms',
    'crispy_bootstrap5',
]

if ENABLE_AZURE_AD:
    INSTALLED_APPS.append('allauth.socialaccount.providers.microsoft')

if ENABLE_CAS and 'cas' not in INSTALLED_APPS:
    INSTALLED_APPS.append('cas')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'cas.middleware.ProxyMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if ENABLE_CAS:
    MIDDLEWARE.insert(3, 'cas.middleware.ProxyMiddleware')
    MIDDLEWARE.append('cas.middleware.CASMiddleware')

ROOT_URLCONF = 'project_intake.urls'

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
                'projects.context_processors.user_permissions',
            ],
        },
    },
]

WSGI_APPLICATION = 'project_intake.wsgi.application'

# Database configuration
use_local_sqlite = os.getenv('USE_LOCAL_SQLITE', 'false').lower() in ('1', 'true', 'yes')
has_postgres_password = bool(os.getenv('POSTGRES_PASSWORD'))

if use_local_sqlite or not has_postgres_password:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'governance_db'),
            'USER': os.getenv('POSTGRES_USER', 'csmart'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
            'HOST': os.getenv('POSTGRES_HOST', 'az-westus2-eis-postgres1.postgres.database.azure.com'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and media files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'projects/static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Auth redirects
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

if ENABLE_AZURE_AD:
    AUTHENTICATION_BACKENDS.append('allauth.account.auth_backends.AuthenticationBackend')

if ENABLE_CAS:
    AUTHENTICATION_BACKENDS.append('cas.backends.CASBackend')

AUTHENTICATION_BACKENDS = tuple(AUTHENTICATION_BACKENDS)

SITE_ID = int(os.getenv('DJANGO_SITE_ID', '1'))

# Azure AD configuration
AZURE_AD_GROUP_MAPPING = {}

if ENABLE_AZURE_AD:
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_USERNAME_REQUIRED = False
    ACCOUNT_AUTHENTICATION_METHOD = 'email'
    ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
    ACCOUNT_LOGOUT_ON_GET = True
    ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
    ACCOUNT_LOGOUT_REDIRECT_URL = '/'
    ACCOUNT_LOGIN_METHODS = {'email'}
    ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']

    SOCIALACCOUNT_STORE_TOKENS = True
    SOCIALACCOUNT_PROVIDERS = {}

    AZURE_AD_TENANT_ID = os.getenv('DJANGO_AZURE_TENANT_ID', 'common')
    AZURE_AD_CLIENT_ID = os.getenv('DJANGO_AZURE_CLIENT_ID', '')
    AZURE_AD_CLIENT_SECRET = os.getenv('DJANGO_AZURE_CLIENT_SECRET', '')
    AZURE_AD_GROUP_MAPPING_RAW = os.getenv('DJANGO_AZURE_GROUP_MAPPING', '')

    AZURE_AD_SCOPES = [
        'openid',
        'email',
        'profile',
        'offline_access',
        'User.Read',
        'GroupMember.Read.All',
    ]

    if AZURE_AD_GROUP_MAPPING_RAW:
        for item in AZURE_AD_GROUP_MAPPING_RAW.split(','):
            key, _, value = item.partition(':')
            if key and value:
                AZURE_AD_GROUP_MAPPING[key.strip()] = value.strip()

    SOCIALACCOUNT_PROVIDERS['microsoft'] = {
        'TENANT': AZURE_AD_TENANT_ID,
        'SCOPE': AZURE_AD_SCOPES,
        'AUTH_PARAMS': {'prompt': 'select_account'},
        'METHOD': 'oauth2',
        'VERIFIED_EMAIL': True,
        'APP': {
            'client_id': AZURE_AD_CLIENT_ID,
            'secret': AZURE_AD_CLIENT_SECRET,
        },
    }
else:
    SOCIALACCOUNT_STORE_TOKENS = False
    SOCIALACCOUNT_PROVIDERS = {}

# CAS configuration
if ENABLE_CAS:
    CAS_SERVER_URL = os.getenv('DJANGO_CAS_SERVER_URL', 'https://cas.coloradocollege.edu/cas/')
    CAS_LOGOUT_COMPLETELY = True
    CAS_PROVIDE_URL_TO_LOGOUT = True
    CAS_GATEWAY = False
    CAS_VERSION = '3'
    CAS_ADMIN_PREFIX = '/admin'
    CAS_CREATE_USER = True
    CAS_AUTO_CREATE_USERS = True
    CAS_IGNORE_REFERER = True
    CAS_REDIRECT_URL = os.getenv('DJANGO_CAS_REDIRECT_URL', 'https://governance.coloradocollege.app')
    CAS_RENAME_ATTRIBUTES = {
        'msDS-cloudExtensionAttribute1': 'username',
        'mail': 'email',
        'givenName': 'first_name',
        'sn': 'last_name',
        'fullName': 'full_name',
        'title': 'title',
        'department': 'department',
    }

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_AGE = 3600
    SESSION_SAVE_EVERY_REQUEST = True

    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Lax'
    CSRF_TRUSTED_ORIGINS.append('https://cas.coloradocollege.edu')

    if DEBUG:
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
                'file': {
                    'level': 'DEBUG',
                    'class': 'logging.FileHandler',
                    'filename': BASE_DIR / 'debug.log',
                    'formatter': 'verbose',
                },
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple',
                },
            },
            'loggers': {
                'django': {
                    'handlers': ['file', 'console'],
                    'level': 'INFO',
                    'propagate': True,
                },
                'projects': {
                    'handlers': ['file', 'console'],
                    'level': 'DEBUG',
                    'propagate': True,
                },
                'cas': {
                    'handlers': ['file', 'console'],
                    'level': 'DEBUG',
                    'propagate': True,
                },
            },
        }
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }

