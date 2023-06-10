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
    def prepare_table_name(dynamic_model_instance):
        return f'dynamic_{dynamic_model_instance.title.lower()}'

    @staticmethod
    def prepare_fields(dynamic_model_instance):
        model_fields = {
            'id': models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
        }

        for field in dynamic_model_instance.fields:
            field_type = field['type']
            field_name = field['title']
            field_class = DynamicModelService.fields_map[field_type]['class']
            model_fields[field_name] = field_class()

        return model_fields

    @staticmethod
    def create_model_class(dynamic_model_instance):
        model_name = dynamic_model_instance.title
        model_fields = DynamicModelService.prepare_fields(dynamic_model_instance)
        table_name = DynamicModelService.prepare_table_name(dynamic_model_instance)
        model_meta = type('Meta', (), {'db_table': table_name})
        model_attrs = {'__module__': 'core.dynamic_models', 'Meta': model_meta, **model_fields}
        model_class = type(model_name, (models.Model,), model_attrs)
        return model_class

    @staticmethod
    def get_or_create_model_class(dynamic_model_instance):
        try:
            model_class = apps.get_model(app_label='core', model_name=dynamic_model_instance.title)
        except LookupError:
            model_class = DynamicModelService.create_model_class(dynamic_model_instance)
        return model_class

    @staticmethod
    def prepare_existing_models_on_ready():
        for model_instance in DynamicModel.objects.all():
            DynamicModelService.create_model_class(model_instance)

    @staticmethod
    def create_table_for_model(dynamic_model_instance):
        prepared_model = DynamicModelService.create_model_class(dynamic_model_instance)

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(prepared_model)
