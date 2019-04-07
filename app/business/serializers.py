from rest_framework import serializers

from core.models import Category, Service, Business


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category object"""

    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service object"""

    class Meta:
        model = Service
        fields = ('id', 'name')
        read_only_fields = ('id',)


class BusinessSerializer(serializers.ModelSerializer):
    """Serializer for Business object"""
    services = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Service.objects.all()
    )
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all()
    )

    class Meta:
        model = Business
        fields = ('id', 'name', 'services', 'categories')
        read_only_fields = ('id',)


class BusinessDetailSerializer(BusinessSerializer):
    """Serializer for Business Detail object"""
    services = ServiceSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
