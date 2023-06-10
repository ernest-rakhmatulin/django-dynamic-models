from django.apps import AppConfig
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from core.services import DynamicModelService

        # Generating the migration plan for Core application
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes(CoreConfig.name)
        migrations_to_apply = executor.migration_plan(targets)

        # If there are no migrations to apply (i.e., all migrations have been already applied)
        if not migrations_to_apply:
            DynamicModelService.prepare_existing_models_on_ready()
