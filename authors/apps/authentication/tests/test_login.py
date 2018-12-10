import pytest

from rest_framework.reverse import reverse

from authors.apps.authentication.models import User
from authors.apps.authentication.tests.factories import authentication


@pytest.mark.django_db
class TestLogin:
    """
    Test cases for user login
    """
    test_user = authentication.UserFactory.create()
    user = {
        "user": {
            "username": test_user.username,
            "email": test_user.email,
            "password": test_user.password
        }
    }

    def test_login_endpoint_with_inactive_account(self, test_client):
        """
        This tests user cannot login if the account is not acttivated
        """
        User.objects.create_user(**self.user['user'])
        assert User.objects.count() > 0

        response = test_client.post(
                                        reverse('login'),
                                        data=self.user, format='json')
        assert response.status_code == 400

    def test_login_endpoint_with_active_account(self, test_client):
        """
        This tests user cannot login if the account is not acttivated
        """
        User.objects.create_user(**self.user['user'])
        user = User.objects.get(email=self.user['user']['email'])
        user.is_active = True
        user.save()
        assert User.objects.count() > 0

        response = test_client.post(
                                        reverse('login'),
                                        data=self.user, format='json')
        assert response.status_code == 200
