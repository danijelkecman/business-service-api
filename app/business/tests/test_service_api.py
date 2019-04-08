from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Service, Business

from ..serializers import ServiceSerializer


SERVICE_URL = reverse('business:service-list')


class PublicServiceApiTests(TestCase):
    """Test the publicly available Service API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(SERVICE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    

class PrivateSeviceApiTests(TestCase):
    """Test the private Service API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            '12345'
        )
        self.client.force_authenticate(self.user)
    
    def test_retrieve_services_list(self):
        """Retrieving a list of services"""
        Service.objects.create(user=self.user, name='Programming')
        Service.objects.create(user=self.user, name='Architect')

        res = self.client.get(SERVICE_URL)

        services = Service.objects.all().order_by('-name')
        serializer = ServiceSerializer(services, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_limited_to_user(self):
        """Test that only services for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'test1@test.com',
            '12345'
        )
        Service.objects.create(user=user2, name='DevOp')
        service = Service.objects.create(user=self.user, name='Frontend')

        res = self.client.get(SERVICE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], service.name)

    def test_create_service_sucessful(self):
        """Test creating a new service"""
        payload = {'name': 'test service'}
        self.client.post(SERVICE_URL, payload)

        exists = Service.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_service_invalid(self):
        """Test creating a new service with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(SERVICE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_services_assigned_to_businesses(self):
        """Test filtering services by thoser assigned to businesses"""
        services1 = Service.objects.create(user=self.user, name='Service 1')
        services2 = Service.objects.create(user=self.user, name='Service 2')
        business = Business.objects.create(user=self.user, name='Business 1')
        business.services.add(services1)

        res = self.client.get(SERVICE_URL, {'assigned_only': 1})

        serializer1 = ServiceSerializer(services1)
        serializer2 = ServiceSerializer(services2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)




    
