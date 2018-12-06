import pytest
from faker import Factory
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
        """
        test user model methods
        :return:
        """
        assert self.test_user.__str__() == self.test_user.email
        assert self.test_user.get_full_name == self.test_user.username
        assert self.test_user.get_short_name() == self.test_user.username

    def test_create_super_user(self):
        su = User.objects.create_superuser(**self.user['user'])
        assert su.is_active is True
        assert su.is_staff is True
        assert su.is_superuser is True

    def test_user_registration(self, test_client):
        response = test_client.post(
            reverse('register'),
            data=self.user,
            format='json')
        assert response.status_code is 201
        assert User.objects.count() > 0

    def test_token_in_response(self, test_client):
        response = test_client.post(
            reverse('register'), self.user, format='json')

        assert isinstance(response.data, dict)
        assert 'username' in response.data
        assert 'token' in response.data

    def test_add_existing_user(self, test_client):
        response = test_client.post(
            reverse('register'), self.user, format='json')

        assert isinstance(response.data, dict)
        assert 'username' in response.data
        response2 = test_client.post(
            reverse('register'), self.user, format='json')
        assert response2.status_code == 400
        assert 'errors' in response2.data
        assert response2.data['errors']['email'][0] == \
            "user with this email already exists."
        assert response2.data['errors']['username'][0] == \
            "user with this username already exists."
