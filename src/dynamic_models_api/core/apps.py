from django.apps import AppConfig
from django.db import connection


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from core.services import DynamicModelService
        from core.models import DynamicModel

        # Check if the table associated with the DynamicModel exists in the database
        table_exists = DynamicModel._meta.db_table in connection.introspection.table_names()

        # If the table exists, call a service method to load dynamic models
        if table_exists:
            DynamicModelService.prepare_existing_models_on_ready()
