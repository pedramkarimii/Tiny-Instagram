from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'

    def ready(self):
        from core import signals
        """
        Executes code when the application is ready.
        This method is called as soon as Django starts.
        Importing the 'signals' module from the 'core' app.
        signal handlers for model signals 'post_save'.
        """
