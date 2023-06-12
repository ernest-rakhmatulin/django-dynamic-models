from django.apps import apps
from django.db import connection
from django.db import models
from rest_framework import serializers

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

        for name, field in model_fields.items():
            field.set_attributes_from_name(name)

        return model_fields

    @staticmethod
    def create_model_class(model_instance):
        model_fields = DynamicModelService.prepare_fields(model_instance)
        table_name = DynamicModelService.prepare_table_name(model_instance)
        
        model_meta = type('Meta', (), {'db_table': table_name})
        model_class = type(model_instance.name, (models.Model,), {
            '__module__': 'core.runtime_generated',
            'Meta': model_meta,
            **model_fields
        })

        return model_class

    @staticmethod
    def create_serializer_class(model_instance):
        model_class = DynamicModelService.get_or_create_model_class(model_instance)

        serializer_meta = type('Meta', (), {
            '__module__': 'core.runtime_generated',
            'model': model_class,
            'fields': '__all__'
        })
        serializer_class = type(f"{model_class.__name__}Serializer", (serializers.ModelSerializer,), {
            '__module__': 'core.runtime_generated',
            'Meta': serializer_meta
        })

        return serializer_class

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

    @staticmethod
    def update_table_for_model(model_instance):
        model_class = apps.get_model(app_label='core', model_name=model_instance.name)

        existing_fields = {field.name: field for field in model_class._meta.get_fields()}
        updated_fields = DynamicModelService.prepare_fields(model_instance)

        existing_keys = set(existing_fields.keys())
        updated_keys = set(updated_fields.keys())

        existing_only = existing_keys - updated_keys
        updated_only = updated_keys - existing_keys
        intersection_keys = existing_keys & updated_keys

        with connection.schema_editor() as schema_editor:
            for field in existing_only:
                schema_editor.remove_field(model_class, existing_fields[field])
            for field in updated_only:
                schema_editor.add_field(model_class, updated_fields[field])
            for field in intersection_keys:
                schema_editor.alter_field(model_class, existing_fields[field], updated_fields[field])

        # Clear the app registry cache to reflect the changes
        apps.clear_cache()
        # Create the updated model class based on the model instance
        DynamicModelService.create_model_class(model_instance)
