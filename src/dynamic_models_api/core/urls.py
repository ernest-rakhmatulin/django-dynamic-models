from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DynamicModelViewSet

router = DefaultRouter()
router.register(r'table', DynamicModelViewSet, basename='dynamic_table')

urlpatterns = [
    path('', include(router.urls)),
]