from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('services', views.ServiceViewSet)

app_name = 'business'

urlpatterns = [
    path('', include(router.urls))
]
