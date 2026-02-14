from django.apps import AppConfig


class UserAccountAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_account_app"

    def ready(self):
        import user_account_app.signals