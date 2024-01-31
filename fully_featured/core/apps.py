from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fully_featured.core"

    def ready(self):
        import fully_featured.core.signals
