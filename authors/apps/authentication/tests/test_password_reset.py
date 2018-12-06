import pytest
from rest_framework.reverse import reverse
from authors.apps.authentication.models import User
from authors.apps.authentication.backends import JWTAuthentication

# instance of authorization class
auth = JWTAuthentication()


@pytest.mark.django_db
class TestResetPassword():

    user = {
        "username": "test_user",
        "email": "testuser@gmail.com",
        "password": "Test@user1"
    }

    def test_registered_user_get_reset_email(self, test_client):
        User.objects.create_user(**self.user)

        response = test_client.post(
            reverse('reset_password'), data={
                "email": self.user['email']}, format='json')
        assert response.status_code == 200

    def test_non_registered_user_request_reset(self, test_client):
        email = "unregistered@mail.com"
        response = test_client.post(
            reverse('reset_password'), data={
                "email": email}, format='json')
        assert response.status_code == 404

    def test_if_no_email_is_provided(self, test_client):
        email = ""
        response = test_client.post(
            reverse('reset_password'), data={
                "email": email}, format='json')
        assert response.status_code == 400

    def test_non_user_registered_reset_password(self, test_client):
        token = auth.generate_reset_token(self.user['email'])
        new_password = "test@1234"

        response = test_client.put(reverse('reset_password_confirm',
                                           kwargs={"token": token}), data={
            "password": new_password}, format='json')
        assert response.status_code == 400
