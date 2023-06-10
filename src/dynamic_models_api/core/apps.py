from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from core.services import DynamicModelService
        DynamicModelService.prepare_existing_models_on_ready()
