from django.test import TestCase
from django.db import models
from django.apps import apps

from rest_framework import serializers
from core.models import DynamicModel
from core.services import DynamicModelService


class DynamicModelServiceTestCase(TestCase):
    def setUp(self):
        self.model_instance = DynamicModel(name='TestModel', fields=[
            {'name': 'string_field', 'type': 'string'},
            {'name': 'number_field', 'type': 'number'},
            {'name': 'boolean_field', 'type': 'boolean'},
        ])
        self.model_instance.save()

    def test_get_choices(self):
        choices = DynamicModelService.get_choices()
        expected_choices = ['string', 'number', 'boolean']
        self.assertEqual(choices, expected_choices)

    def test_prepare_table_name(self):
        table_name = DynamicModelService.prepare_table_name(self.model_instance)
        expected_table_name = 'dynamic_testmodel'
        self.assertEqual(table_name, expected_table_name)

    def test_prepare_fields(self):
        fields = DynamicModelService.prepare_fields(self.model_instance)
        expected_fields = {
            'id': models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
            'string_field': models.TextField(),
            'number_field': models.FloatField(),
            'boolean_field': models.BooleanField()
        }
        field_types = {k: v.__class__.__name__ for k, v in fields.items()}
        expected_field_types = {k: v.__class__.__name__ for k, v in expected_fields.items()}
        self.assertDictEqual(field_types, expected_field_types)

    def test_create_model_class(self):
        model_class = DynamicModelService.create_model_class(self.model_instance)
        self.assertTrue(issubclass(model_class, models.Model))
        self.assertEqual(model_class.__name__, 'TestModel')
        self.assertEqual(model_class._meta.db_table, 'dynamic_testmodel')

        fields = model_class._meta.get_fields()
        field_names = [field.name for field in fields]
        self.assertCountEqual(field_names, ['id', 'string_field', 'number_field', 'boolean_field'])

    def test_create_serializer_class(self):
        serializer_class = DynamicModelService.create_serializer_class(self.model_instance)
        self.assertTrue(issubclass(serializer_class, serializers.ModelSerializer))
        self.assertEqual(serializer_class.Meta.model.__name__, 'TestModel')
        self.assertEqual(serializer_class.Meta.fields, '__all__')

    def test_get_or_create_model_class(self):
        existing_model = DynamicModel(name='ExistingModel', fields=[])
        existing_model.save()

        not_existing_model = DynamicModel(name='NotExistingModel', fields=[])
        not_existing_model.save()

        DynamicModelService.create_model_class(existing_model)
        model_class = DynamicModelService.get_or_create_model_class(existing_model)
        self.assertEqual(model_class.__name__, 'ExistingModel')
        model_class = DynamicModelService.get_or_create_model_class(not_existing_model)
        self.assertEqual(model_class.__name__, 'NotExistingModel')

    def test_update_table_for_model_removes_fields(self):
        # Create the initial table
        DynamicModelService.create_table_for_model(self.model_instance)

        # Remove a field from the model instance
        self.model_instance.fields.pop(0)
        self.model_instance.save()
        # Update the table for the model
        DynamicModelService.update_table_for_model(self.model_instance)

        # Check if the field has been removed from the table
        model_class = apps.get_model(app_label='core', model_name='TestModel')
        field_names = [field.name for field in model_class._meta.get_fields()]
        self.assertNotIn('string_field', field_names)

    def test_update_table_for_model_adds_fields(self):
        # Create the initial table
        DynamicModelService.create_table_for_model(self.model_instance)

        # Add a new field to the model instance
        self.model_instance.fields.append({'name': 'new_field', 'type': 'string'})

        # Update the table for the model
        DynamicModelService.update_table_for_model(self.model_instance)

        # Check if the new field has been added to the table
        model_class = apps.get_model(app_label='core', model_name='TestModel')
        field_names = [field.name for field in model_class._meta.get_fields()]
        self.assertIn('new_field', field_names)

    def test_update_table_for_model_alters_fields(self):
        # Create the initial table
        DynamicModelService.create_table_for_model(self.model_instance)

        # Modify an existing field (number field to be a string) in the model instance
        self.model_instance.fields[1]['type'] = 'string'

        # Update the table for the model
        DynamicModelService.update_table_for_model(self.model_instance)

        # Check if the field name has been updated in the table
        model_class = apps.get_model(app_label='core', model_name='TestModel')
        self.assertEquals(
            model_class.number_field.field.__class__,
            DynamicModelService.fields_map['string']['class']
        )
