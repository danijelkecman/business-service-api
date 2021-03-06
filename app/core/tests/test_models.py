from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from .. import models

def sample_user(email='test@test.com', password='12345'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test custom creating a new customuser with an email without username is successful"""
        email = 'test@test.com'
        password = '12345'
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_new_user_with_email_normalized(self):
        """Test that the email for a new user is normalized"""
        email = 'test@TEST.COM'
        user = get_user_model().objects.create_user(
            email = email,
            password = '12345'
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test no email raises email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '12345')

    def test_create_new_superuser(self):
        """Test creating superuser"""
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            '12345'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_category_str(self):
        """Test the category string representation"""
        category = models.Category.objects.create(
            user=sample_user(),
            name='IT'
        )
        
        self.assertEqual(str(category), category.name)

    def test_services_str(self):
        """Test the service model string represenation"""
        service = models.Service.objects.create(
            user=sample_user(),
            name='Programming'
        )
        self.assertEqual(str(service), service.name)

    def test_business_str(self):
        """Test the business model string representation"""
        business = models.Business.objects.create(
            user=sample_user(),
            name='CxRomos'
        )

    @patch('uuid.uuid4')
    def test_business_file_name_uuid(self, mock_uuid):
        """Test that image is saved in correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.business_image_file_path(None, 'business-image.jpg')

        exp_path = f'uploads/business/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)

    

