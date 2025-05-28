from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.auth'

    def ready(self):
        import app.auth.signals  # noqa
