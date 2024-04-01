from django.apps import AppConfig


class PostConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.post'

    def ready(self):
        """
        Override the ready method to import signals when the application is ready.
        """
        from app.post import signals
