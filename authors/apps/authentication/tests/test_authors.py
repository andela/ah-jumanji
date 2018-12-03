from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from ..models import User


def register_user(
        username="Thanos",
        email="thanos@avengers.com",
        password="avengersassemble"):
    """Creating a test user"""
    user = User.objects.create_user(username, email, password)
    thisuser = User.objects.get(email='thanos@avengers.com')
    thisuser.is_active = True
    thisuser.save()
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

    def test_get_all_users(self):
        """Test get all authors"""
        token = self.login_user()
        response = self.client.get(
            '/api/users/',
            HTTP_AUTHORIZATION='Token ' + token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
