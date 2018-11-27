import pytest
from rest_framework.reverse import reverse

from authors.apps.authentication.models import User
from authors.apps.authentication.tests.factories.authentication import UserFactory


@pytest.mark.django_db
class TestLogin:
    """
    Test cases for user login
    """
    test_user = UserFactory.create()
    user = {
        "user": {
            "username": test_user.username,
            "email": test_user.email,
            "password": test_user.password
        }
    }

    def test_login_endpoint(self, test_client):
        User.objects.create_user(**self.user['user'])
        assert User.objects.count() > 0

        response = test_client.post(reverse('login'), data=self.user, format='json')
        assert response.status_code == 200
