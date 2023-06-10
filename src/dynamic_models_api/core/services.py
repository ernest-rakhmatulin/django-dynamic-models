from django.apps import apps
from django.db import connection
from django.db import models

from core.models import DynamicModel


class DynamicModelService:

    fields_map = {
        'string': {
            'class': models.TextField,
        },
        'number': {
            'class': models.FloatField,
        },
        'boolean': {
            'class': models.BooleanField,
        },
    }

    @staticmethod
    def get_choices():
        return list(DynamicModelService.fields_map.keys())

    @staticmethod
    def prepare_table_name(model_instance):
        return f'dynamic_{model_instance.name.lower()}'

    @staticmethod
    def prepare_fields(model_instance):
        model_fields = {
            'id': models.BigAutoField(auto_created=True, primary_key=True, serialize=False)
        }

        for field in model_instance.fields:
            field_class = DynamicModelService.fields_map[field['type']]['class']
            model_fields[field['name']] = field_class()

        return model_fields

    @staticmethod
    def create_model_class(model_instance):
        model_fields = DynamicModelService.prepare_fields(model_instance)
        table_name = DynamicModelService.prepare_table_name(model_instance)
        
        model_meta = type('Meta', (), {'db_table': table_name})
        model_attrs = {'__module__': 'core.dynamic_models', 'Meta': model_meta, **model_fields}
        model_class = type(model_instance.name, (models.Model,), model_attrs)
        
        return model_class

    @staticmethod
    def get_or_create_model_class(model_instance):
        try:
            model_class = apps.get_model(app_label='core', model_name=model_instance.name)
        except LookupError:
            model_class = DynamicModelService.create_model_class(model_instance)
        return model_class

    @staticmethod
    def prepare_existing_models_on_ready():
        for model_instance in DynamicModel.objects.all():
            DynamicModelService.create_model_class(model_instance)

    @staticmethod
    def create_table_for_model(model_instance):
        prepared_model = DynamicModelService.create_model_class(model_instance)

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(prepared_model)
