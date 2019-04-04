from rest_framework import serializers

from core.models import Category, Service


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category object"""

    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ServiceSerializer(serializers.ModelSerializer):
    """Serizlier for Service object"""

    class Meta:
        model = Service
        fields = ('id', 'name')
        read_only_fields = ('id',)