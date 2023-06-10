from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import DynamicModel
from .serializers import DynamicModelSerializer
from .services import DynamicModelService

class DynamicModelViewSet(ModelViewSet):
    queryset = DynamicModel.objects.all()
    serializer_class = DynamicModelSerializer

    @action(detail=True, methods=['post'])
    def row(self, request, pk=None):
        model_instance = self.get_object()
        serializer_class = DynamicModelService.create_serializer_class(model_instance)
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def rows(self, request, pk=None):
        model_instance = self.get_object()
        serializer_class = DynamicModelService.create_serializer_class(model_instance)
        model_class = DynamicModelService.get_or_create_model_class(model_instance)

        objects = model_class.objects.all()
        serializer = serializer_class(instance=objects, many=True)
        return Response(serializer.data)
