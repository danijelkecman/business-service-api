import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Business, Category, Service

from ..serializers import BusinessSerializer, BusinessDetailSerializer


BUSINESS_URL = reverse('business:business-list')


def image_upload_url(business_id):
    """Return url for business image"""
    return reverse('business:business-upload-image', args=[business_id])

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


class BusinessImageUploadTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user@test.com', '12345')
        self.client.force_authenticate(self.user)
        self.business = sample_business(user=self.user)

    def tearDown(self):
        self.business.image.delete()

    def test_upload_image_to_business(self):
        """Test uploading an image to business"""
        url = image_upload_url(self.business.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')
        
        self.business.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.business.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.business.id)

        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_businesses_by_category(self):
        """Test returning businesses in specific category"""
        business1 = sample_business(user=self.user, name='Business 1')
        business2 = sample_business(user=self.user, name='Business 2')
        category1 = sample_category(user=self.user, name='Category 1')
        category2 = sample_category(user=self.user, name='Category 2')
        business1.categories.add(category1)
        business2.categories.add(category2)
        business3 = sample_business(user=self.user, name='Business 3')

        res = self.client.get(
            BUSINESS_URL,
            {'categories': f'{category1.id}, {category2.id}'}
        )

        serializer1 = BusinessSerializer(business1)
        serializer2 = BusinessSerializer(business2)
        serializer3 = BusinessSerializer(business3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_businesses_by_services(self):
        """Test returning businesses in specific service"""
        business1 = sample_business(user=self.user, name='Business 1')
        business2 = sample_business(user=self.user, name='Business 2')
        service1 = sample_service(user=self.user, name='Service 1')
        service2 = sample_service(user=self.user, name='Service 2')
        business1.services.add(service1)
        business2.services.add(service2)
        business3 = sample_business(user=self.user, name='Business 3')

        res = self.client.get(
            BUSINESS_URL,
            {'services': f'{service1.id}, {service2.id}'}
        )

        serializer1 = BusinessSerializer(business1)
        serializer2 = BusinessSerializer(business2)
        serializer3 = BusinessSerializer(business3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    
        