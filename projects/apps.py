from django.apps import AppConfig
from django.conf import settings


class ProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'
    
    def ready(self):
        # Import CAS-related signals only when CAS is enabled
        if getattr(settings, "ENABLE_CAS", False):
            from . import cas_signals  # noqa: F401
