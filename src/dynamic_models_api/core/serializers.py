from rest_framework import serializers
from django.db import transaction
from .models import DynamicModel
from .services import DynamicModelService


class FieldSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=DynamicModelService.get_choices())


class DynamicModelSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True)

    class Meta:
        model = DynamicModel
        fields = '__all__'
        read_only_fields = ['pk']

    @transaction.atomic()
    def create(self, validated_data):
        instance = super().create(validated_data)
        DynamicModelService.create_table_for_model(instance)
        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        DynamicModelService.update_table_for_model(instance)
        return instance
