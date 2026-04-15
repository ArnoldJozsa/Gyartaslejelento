from django.apps import AppConfig

class GyartasAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gyartas_app'

    def ready(self):
        pass  # signals.py már nincs, ezért nem importáljuk
