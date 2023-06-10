from rest_framework.viewsets import ModelViewSet

from .models import DynamicModel
from .serializers import DynamicModelSerializer


class DynamicModelViewSet(ModelViewSet):
    queryset = DynamicModel.objects.all()
    serializer_class = DynamicModelSerializer
