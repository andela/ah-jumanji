from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from authors.apps.authentication.models import User


def register_user(
        username="Thanos",
        email="thanos@avengers.com",
        password="avengersassemble"):
    """Creating a test user"""
    user = User.objects.create_user(username, email, password)
    return user


class TestProfile(TestCase):
    """Test profile."""

    def setUp(self):
        """Test Setup."""
        self.client = APIClient()
        self.login_credentials = {
            'user': {
                'email': "thanos@avengers.com",
                'password': "avengersassemble"
            }
        }

    def login_user(self):
        """Login A user"""
        register_user()
        response = self.client.post(
            '/api/users/login',
            data=self.login_credentials,
            format='json',
        )
        return response.data['token']

    def test_get_all_user_profiles(self):
        """Test get all user profiles"""
        token = self.login_user()
        response = self.client.get(
            '/api/profiles/',
            format='json',
            HTTP_AUTHORIZATION='Token ' + token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_not_existing_user_profile(self):
        """Test get not existing user profile"""
        token = self.login_user()
        response = self.client.get(
            '/api/profiles/Hulk',
            format='json',
            HTTP_AUTHORIZATION='Token ' + token
        )
        self.assertEqual(response.status_code, 404)

    def test_get_existing_user_profile(self):
        """Test get existing user profile"""
        token = self.login_user()
        response = self.client.get(
            '/api/profiles/Thanos',
            format='json',
            HTTP_AUTHORIZATION='Token ' + token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
