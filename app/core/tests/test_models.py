from django.test import TestCase
from django.contrib.auth import get_user_model


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
