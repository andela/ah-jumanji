from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework.test import (
    APIClient, APIRequestFactory
)
from rest_framework import status

from ..models import User
from ..backends import account_activation_token


class AccountActivationTestCase(TestCase):
    """
    This class defines tests for user account activation view
    """

    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()

        self.user = {
            'user': {
                'username': 'fabish',
                'email': 'fabish.olasi@andela.com',
                'password': 'secretsantaS#3'
            }
        }

        self.user_2 = {
            'user': {
                'username': 'jimmy',
                'email': 'jimmy@example.com',
                'password': 'secretsantaS#3'
            }
        }

    def sign_user(self, user_data):
        response = self.client.post(
                                        reverse('register'),
                                        user_data, format='json')
        return response

    def test_email_sent_to_new_user(self):

        self.client.post(
            '/api/users/register',
            self.user,
            format='json'
        )
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.subject, 'Activate your account.')

    def test_email_not_sent_if_invalid(self):
        self.client.post(
            'api/users/register',
            self.user_2,
            format='json'
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_link_activation_successful(self):
        self.sign_user(self.user)
        details = User.objects.get(username=self.user['user']['username'])
        pk = urlsafe_base64_encode(force_bytes(details.id)).decode()
        token = account_activation_token.make_token(details)
        protocol = 'http://'
        path = 'api/users/activate/'
        url = '{0}localhost:8000/{1}{pk}/{token}'.format(
                                                            protocol,
                                                            path,
                                                            pk=pk,
                                                            token=token)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
