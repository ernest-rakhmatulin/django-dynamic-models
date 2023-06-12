from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from django.apps import apps
from django.db import connection
from django.db import models
from django.db.utils import DataError
from rest_framework import serializers

from core.models import DynamicModel


DynamicModelType = TypeVar('DynamicModelType')
DynamicModelSerializerType = TypeVar('DynamicModelSerializerType')


class DynamicModelService:
    FIELDS_MAP: Dict[str, Type[models.Field]] = {
        'string': models.TextField,
        'number': models.FloatField,
        'boolean': models.BooleanField,
    }

    @staticmethod
    def get_choices() -> List[str]:
        """Return a list of available field choices."""
        return list(DynamicModelService.FIELDS_MAP.keys())

    @staticmethod
    def prepare_table_name(model_instance: DynamicModel) -> str:
        """
        Prepare the table name for the dynamic model based
        on the model instance name.
        """
        return f'dynamic_{model_instance.name.lower()}'

    @staticmethod
    def prepare_fields(model_instance: DynamicModel) -> Dict[str, models.Field]:
        """
        Prepare the model fields for the dynamic model based on the
        field definitions in the model instance.
        """
        model_fields: Dict[str, models.Field] = dict()

        for field in model_instance.fields:
            field_type = field['type']
            field_class = DynamicModelService.FIELDS_MAP.get(field_type)
            if field_class:
                model_fields[field['name']] = field_class()

        for name, field in model_fields.items():
            field.set_attributes_from_name(name)

        return model_fields

    @staticmethod
    def create_model_class(model_instance: DynamicModel) -> DynamicModelType:
        """
        Create a dynamic model class based on the model instance.
        """
        table_name = DynamicModelService.prepare_table_name(model_instance)
        model_fields = DynamicModelService.prepare_fields(model_instance)

        model_meta = type('Meta', (), {'db_table': table_name})
        model_class = type(model_instance.name, (models.Model,), {
            '__module__': 'core.runtime_generated',
            'Meta': model_meta,
            **model_fields
        })

        return model_class

    @staticmethod
    def create_serializer_class(model_instance: DynamicModel) -> DynamicModelSerializerType:
        """
        Create a serializer class for the dynamic model based on the model instance.
        """
        model_class = DynamicModelService.get_or_create_model_class(model_instance)

        serializer_meta = type('Meta', (), {
            'model': model_class,
            'fields': '__all__'
        })
        serializer_class = type(f"{model_class.__name__}Serializer", (serializers.ModelSerializer,), {
            '__module__': 'core.runtime_generated',
            'Meta': serializer_meta
        })

        return serializer_class

    @staticmethod
    def get_or_create_model_class(model_instance: DynamicModel) -> DynamicModelType:
        """
        Get or create a model class for the dynamic model based on the
        model instance.
        """
        try:
            model_class = apps.get_model(app_label='core', model_name=model_instance.name)
        except LookupError:
            model_class = DynamicModelService.create_model_class(model_instance)
        return model_class

    @staticmethod
    def prepare_existing_models_on_ready() -> None:
        """
        This method is intended to be used in the `ready` method of
        the `CoreConfig` class in the app's AppConfig.

        It creates model classes for all existing DynamicModel
        instances on start or restart of the application.
        """
        for model_instance in DynamicModel.objects.all():
            DynamicModelService.create_model_class(model_instance)

    @staticmethod
    def create_table_for_model(model_instance: DynamicModel) -> None:
        """
        Create a database table for the dynamic model.
        """
        prepared_model = DynamicModelService.create_model_class(model_instance)

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(prepared_model)

    @staticmethod
    def update_table_for_model(model_instance: DynamicModel) -> None:
        """
        Update the database table schema for a dynamic model based
        on the changes in the model instance.
        """
        model_class = apps.get_model(app_label='core', model_name=model_instance.name)
        existing_fields = {field.name: field for field in model_class._meta.get_fields()}
        updated_fields = DynamicModelService.prepare_fields(model_instance)
        existing_keys = set(existing_fields.keys())
        updated_keys = set(updated_fields.keys())

        fields_to_remove = existing_keys - updated_keys
        fields_to_add = updated_keys - existing_keys
        fields_to_alter = existing_keys & updated_keys

        with connection.schema_editor() as schema_editor:
            for field_name in fields_to_remove:
                schema_editor.remove_field(model_class, existing_fields[field_name])
            for field_name in fields_to_add:
                schema_editor.add_field(model_class, updated_fields[field_name])
            for field_name in fields_to_alter:
                try:
                    schema_editor.alter_field(model_class, existing_fields[field_name], updated_fields[field_name])
                except DataError:
                    # If altering the field causes a DataError,
                    # remove the field and add the updated field instead
                    schema_editor.remove_field(model_class, existing_fields[field_name])
                    schema_editor.add_field(model_class, updated_fields[field_name])
        # Clear the app registry cache to reflect the changes
        apps.clear_cache()
        # Create the updated model class based on the model instance
        DynamicModelService.create_model_class(model_instance)
