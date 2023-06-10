from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DynamicModelSerializer
from .models import DynamicModel


class DynamicModelAPIView(APIView):

    def post(self, request):
        serializer = DynamicModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        tables = DynamicModel.objects.all()
        serializer = DynamicModelSerializer(instance=tables, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
