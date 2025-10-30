from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'
    
    def ready(self):
        # Import signals to register them
        import projects.cas_signals
