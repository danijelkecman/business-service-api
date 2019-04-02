from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category

from ..serializers import CategorySerializer


CATEGORY_URL = reverse('business:category-list')


class PublicCategoryApiTests(TestCase):
    """Test the publicly available category API"""
    """Categories are created by staff users via web page admin panel"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving categories"""
        res = self.client.get(CATEGORY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoryApiTests(TestCase):
    """Test the authorized categories API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            '12345'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieving_categories(self):
        """Test retrieving categories"""
        Category.objects.create(user=self.user, name='Programming')
        Category.objects.create(user=self.user, name='Cooking')

        res = self.client.get(CATEGORY_URL)

        categories = Category.objects.all().order_by('-name')
        serializer = CategorySerializer(categories, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_category_limited_to_user(self):
        """Test that categories are limited for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'test1@test.com',
            '12345'
        )
        Category.objects.create(user=user2, name='Driving')
        category = Category.objects.create(user=self.user, name='Nursing')

        res = self.client.get(CATEGORY_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], category.name)

    def test_create_category_sucessful(self):
        """Test creating a new category"""
        payload = {'name': 'test category'}
        self.client.post(CATEGORY_URL, payload)

        exists = Category.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_category_invalid(self):
        """Test creating a new category with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
