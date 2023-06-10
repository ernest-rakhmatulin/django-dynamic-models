from rest_framework import serializers

from .models import DynamicModel
from .services import DynamicModelService


class FieldSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=DynamicModelService.get_choices())


class DynamicModelSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True)

    class Meta:
        model = DynamicModel
        fields = ['pk', 'title', 'fields']
        read_only_fields = ['pk']

    def create(self, validated_data):
        instance = super().create(validated_data)
        DynamicModelService.create_table_for_model(instance)
        return instance
