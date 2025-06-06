# Social Auth Settings
# AUTHENTICATION_BACKENDS = (
#     'django.contrib.auth.backends.ModelBackend',
#     'allauth.account.auth_backends.AuthenticationBackend',
# )

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.sites',
    # 'allauth',
    # 'allauth.account',
    # 'allauth.socialaccount',
    # 'allauth.socialaccount.providers.microsoft',
    'projects',
    'crispy_forms',
    'crispy_bootstrap5',
]

# SITE_ID = 1

# # Azure AD Configuration
# SOCIALACCOUNT_PROVIDERS = {
#     'microsoft': {
#         'TENANT': 'your-tenant-id',  # Replace with your Azure AD tenant ID
#         'SCOPE': ['User.Read', 'GroupMember.Read.All'],
#         'AUTH_PARAMS': {'prompt': 'select_account'},
#         'METHOD': 'oauth2',
#         'VERIFIED_EMAIL': True,
#     }
# }

# # Add the pipeline to the social auth pipeline
# SOCIAL_AUTH_PIPELINE = (
#     'social_core.pipeline.social_auth.social_details',
#     'social_core.pipeline.social_auth.social_uid',
#     'social_core.pipeline.social_auth.auth_allowed',
#     'social_core.pipeline.social_auth.social_user',
#     'social_core.pipeline.user.get_username',
#     'social_core.pipeline.user.create_user',
#     'social_core.pipeline.social_auth.associate_user',
#     'social_core.pipeline.social_auth.load_extra_data',
#     'social_core.pipeline.user.user_details',
#     'projects.auth_pipeline.sync_azure_groups',  # Add our custom pipeline
# )

# # AllAuth Settings
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_USERNAME_REQUIRED = False
# ACCOUNT_AUTHENTICATION_METHOD = 'email'
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
# LOGIN_REDIRECT_URL = '/'
# ACCOUNT_LOGOUT_REDIRECT_URL = '/'
# ACCOUNT_UNIQUE_EMAIL = True
# ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Your App Name] '

# Session Settings
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
CSRF_COOKIE_SECURE = True  # Only send cookie over HTTPS

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gov_project_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',  # Replace with your actual password
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
} 