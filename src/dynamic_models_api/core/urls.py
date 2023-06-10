from django.urls import path
from .views import DynamicModelAPIView

urlpatterns = [
    path('table/', DynamicModelAPIView.as_view(), name='dynamic_table'),
]
