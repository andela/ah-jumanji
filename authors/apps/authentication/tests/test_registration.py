import random
import string

import pytest
from faker import Factory
from rest_framework import status
from rest_framework.reverse import reverse

from authors.apps.authentication.models import User
from .factories.authentication import UserFactory


@pytest.mark.django_db
class TestRegistration:
    """
    Test cases for user login
    """
    faker = Factory.create()
    test_user = UserFactory()
    user = {
        "user": {
            "username": test_user.username,
            "email": test_user.email,
            "password": test_user.password
        }
    }

    def test_user_instance(self):
        """Test user model methods"""
        assert self.test_user.__str__() == self.test_user.email
        assert self.test_user.get_full_name == self.test_user.username
        assert self.test_user.get_short_name() == self.test_user.username

    def test_create_super_user(self):
        """Test super user can be created"""
        su = User.objects.create_superuser(**self.user['user'])
        assert su.is_active is True
        assert su.is_staff is True
        assert su.is_superuser is True

    def test_user_registration(self, test_client):
        """Test successful user registration"""
        response = test_client.post(reverse('register'),
                                    data=self.user, format='json')
        assert response.status_code is 201
        assert User.objects.count() > 0

    def test_token_in_response(self, test_client):
        """Test token is generated and is at the response"""
        response = test_client.post(reverse('register'),
                                    self.user, format='json')

        assert isinstance(response.data, dict)
        assert 'username' in response.data
        assert 'token' in response.data

    def test_add_existing_user(self, test_client):
        """Test API cannot add an existing user"""
        test_client.post(reverse('register'), self.user, format='json')
        res = test_client.post(reverse('register'), self.user, format='json')

        assert res.status_code == 400
        assert 'errors' in res.data

        assert res.data['errors']['email'][0] == 'Email already exists. Sign '\
                                                 'in instead or try another.'
        assert res.data['errors']['username'][0] == 'The username already ' \
                                                    'exists. Kindly try ' \
                                                    'another.'

    def test_user_cannot_register_with_a_blank_email_field(self, test_client):
        """Test the API cannot register a user with blank password field"""
        del self.user['user']['email']
        response = test_client.post(reverse('register'),
                                    self.user, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert response.data['errors']['email'][0] == 'Please fill in the ' \
                                                      'email.'

    def test_user_cannot_register_with_an_invalid_email(self, test_client):
        """Test the API cannot register a user with an invalid email"""
        self.user['user']['email'] = 'WRONG_EMAIL'
        res = test_client.post(reverse('register'), self.user, format='json')

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in res.data
        assert res.data['errors']['email'][0] == 'You have input an invalid ' \
                                                 'email. Kindly check again.'

    def test_user_cannot_register_with_a_short_username(self, test_client):
        """Test the API cannot register a user with a short username"""
        self.user['user']['username'] = 'abc'
        res = test_client.post(reverse('register'), self.user, format='json')

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in res.data
        assert res.data['errors']['username'][0] == 'Username must have a ' \
                                                    'minimum of 4 characters.'

    def test_user_cannot_register_with_a_long_username(self, test_client):
        """Test the API cannot register a user with a long password"""
        chars = string.ascii_letters + string.digits
        uname_size = 31
        username = ''.join((random.choice(chars)) for x in range(uname_size))
        self.user['user']['username'] = username
        res = test_client.post(reverse('register'), self.user, format='json')

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in res.data
        assert res.data['errors']['username'][0] == 'Username must have a ' \
                                                    'maximum of 30 ' \
                                                    'characters.'

    def test_user_cannot_register_with_blank_username_field(self, test_client):
        """Test the API cannot register a user with blank username field"""
        del self.user['user']['username']
        res = test_client.post(reverse('register'), self.user, format='json')

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in res.data
        assert res.data['errors']['username'][0] == 'Please fill in the ' \
                                                    'username.'

    def test_user_cannot_register_with_wrong_username(self, test_client):
        """Test the API cannot register a user with an wrong username format"""
        self.user['user']['username'] = 'wrong username'
        res = test_client.post(reverse('register'), self.user, format='json')

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in res.data
        assert res.data['errors']['username'][0] == 'Username cannot only ' \
                                                    'have alphanumeric ' \
                                                    'characters.'

    def test_user_cannot_register_with_blank_password_field(self, test_client):
        """Test the API cannot register a user with blank password field"""
        del self.user['user']['password']
        res = test_client.post(reverse('register'), self.user, format='json')

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in res.data
        assert res.data['errors']['password'][0] == 'Please fill in the ' \
                                                    'password.'

    def test_user_cannot_register_with_a_short_password(self, test_client):
        """Test the API cannot register a user with a short password"""
        self.user['user']['password'] = 'abc'
        res = test_client.post(reverse('register'), self.user, format='json')

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in res.data
        assert res.data['errors']['password'][0] == 'Password must have a ' \
                                                    'minimum of 8 characters.'

    def test_user_cannot_register_with_a_long_password(self, test_client):
        """Test the API cannot register a user with a long password"""
        chars = string.ascii_letters + string.digits
        pwd_size = 129
        password = ''.join((random.choice(chars)) for x in range(pwd_size))
        self.user['user']['password'] = password
        res = test_client.post(reverse('register'), self.user, format='json')

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in res.data
        assert res.data['errors']['password'][0] == 'Password must have a ' \
                                                    'maximum of 128 ' \
                                                    'characters.'

    def test_unsuccessful_registration_letters_password(self, test_client):
        """Test the API cannot register a user with all letters password"""
        self.user['user']['password'] = 'abcdefgh'
        res = test_client.post(reverse('register'), self.user, format='json')

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in res.data
        assert res.data['errors']['password'][0] == 'Password must contain ' \
                                                    'at least a lowercase ' \
                                                    'letter, an uppercase ' \
                                                    'letter, a number and a ' \
                                                    'special character.'

    def test_unsuccessful_registration_numeric_password(self, test_client):
        """Test the API cannot register a user with all numbers password"""
        self.user['user']['password'] = 12345678
        res = test_client.post(reverse('register'), self.user, format='json')

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in res.data
        assert res.data['errors']['password'][0] == 'Password must contain ' \
                                                    'at least a lowercase ' \
                                                    'letter, an uppercase ' \
                                                    'letter, a number and a ' \
                                                    'special character.'
