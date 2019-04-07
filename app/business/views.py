from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Category, Service, Business
from . import serializers


class BaseBusinessAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """Base viewset for business attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new category"""
        serializer.save(user=self.request.user)


class CategoryViewSet(BaseBusinessAttrViewSet):
    """Manage categories in the database"""
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class ServiceViewSet(BaseBusinessAttrViewSet):
    """Manage services in the database"""
    queryset = Service.objects.all()
    serializer_class = serializers.ServiceSerializer


class BusinessViewSet(viewsets.ModelViewSet):
    """Manage business in the database"""
    serializer_class = serializers.BusinessSerializer
    queryset = Business.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.BusinessDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new business"""
        serializer.save(user=self.request.user)
    