from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Business, Category, Service

from ..serializers import BusinessSerializer, BusinessDetailSerializer


BUSINESS_URL = reverse('business:business-list')


def detail_url(business_id):
    """Return business detail url"""
    return reverse('business:business-detail', args=[business_id])


def sample_category(user, name='Programming'):
    """Create and return a sample category"""
    return Category.objects.create(user=user, name=name)

def sample_service(user, name='iOS'):
    """Create and return sample service"""
    return Service.objects.create(user=user, name=name)


def sample_business(user, **params):
    """Create and return sample businesses"""
    defaults = {
        'name': "Sample Business"
    }
    defaults.update(params)

    return Business.objects.create(user=user, **defaults)


class PublicBusinessApiTest(TestCase):
    """Test unauthenticated business API access"""

    def setUp(self):
        self.client = APIClient()
    

    def test_auth_required(self):
        """Test authentication is required"""
        res = self.client.get(BUSINESS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    

class PrivateBusinessApiTest(TestCase):
    """Test authenticated business API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('test@test.com', '12345')
        self.client.force_authenticate(self.user)

    def test_retrieve_business(self):
        """Test retrieving a list of businesses"""
        sample_business(user=self.user)
        sample_business(user=self.user)

        res = self.client.get(BUSINESS_URL)

        businesses = Business.objects.all().order_by('-id')
        serializer = BusinessSerializer(businesses, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_businesses_limited_to_user(self):
        """Test retrieving businesses for user"""
        user2 = get_user_model().objects.create_user('test1@test.com', '12345')
        sample_business(user=user2)
        sample_business(user=self.user)

        res = self.client.get(BUSINESS_URL)

        businesses = Business.objects.filter(user=self.user)
        serializer = BusinessSerializer(businesses, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_business_detail(self):
        """Test viewing business details"""
        business = sample_business(user=self.user)
        business.categories.add(sample_category(user=self.user))
        business.services.add(sample_service(user=self.user))

        url = detail_url(business.id)
        res = self.client.get(url)

        serializer = BusinessDetailSerializer(business)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_business(self):
        """Test creating business"""
        payload = {
            'name': 'Business 1'
        }
        res = self.client.post(BUSINESS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        business = Business.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(business, key))

    def test_creating_business_with_category(self):
        """Test creating business with a categories"""
        category1 = sample_category(user=self.user, name='Category 1')
        category2 = sample_category(user=self.user, name='Category 2')
        payload = {
            'name': 'Business 1',
            'categories': [category1.id, category2.id]
        }
        res = self.client.post(BUSINESS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        business = Business.objects.get(id=res.data['id'])
        categories = business.categories.all()
        self.assertEqual(categories.count(), 2)
        self.assertIn(category1, categories)
        self.assertIn(category2, categories)

    def test_creating_business_with_service(self):
        """Test creating business with services"""
        service1 = sample_service(user=self.user, name='Service 1')
        service2 = sample_service(user=self.user, name='Service 2')
        payload = {
            'name': 'Business 1',
            'services': [service1.id, service2.id]
        }
        res = self.client.post(BUSINESS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        business = Business.objects.get(id=res.data['id'])
        services = business.services.all()
        self.assertEqual(services.count(), 2)
        self.assertIn(service1, services)
        self.assertIn(service2, services)

    def test_partial_update_business(self):
        """Test updating a business with patch"""
        business = sample_business(user=self.user)
        business.categories.add(sample_category(user=self.user))
        newCategory = sample_category(user=self.user, name='Category 2')

        payload = {
            'name': 'Sample Business 1',
            'categories': [newCategory.id]
        }
        url = detail_url(business.id)
        res = self.client.patch(url, payload)

        business.refresh_from_db()

        self.assertEqual(business.name, payload['name'])
        categories = business.categories.all()
        self.assertEqual(categories.count(), 1)

    def test_full_update_business(self):
        """Test updating a business with patch"""
        business = sample_business(user=self.user)
        business.categories.add(sample_category(user=self.user))

        payload = {
            'name': 'Sample Business 1'
        }
        url = detail_url(business.id)
        res = self.client.put(url, payload)

        business.refresh_from_db()

        self.assertEqual(business.name, payload['name'])
        categories = business.categories.all()
        self.assertEqual(categories.count(), 0)
