import json
import logging

from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

logger = logging.getLogger(__file__)


class TestGetEndpoint(APITestCase):

    def setUp(self):

        self.token = self.get_user_token()

        self.data = {
            "slug": "posting_test",
            "title": "Posting Test",
            "description": "this is a posting test",
            "body": "The test was successful",
            "tagList": "live again",
            "author": 'TestAuthor'
        }

    def test_postArticle_status(self):

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articles')
        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse('articles')
        response = self.client.get(url)

        response.render()
        self.assertIn(b"posting-test", response.content)
        self.assertIn(b"Posting Test", response.content)
        self.assertIn(b"this is a posting test", response.content)
        self.assertIn(b"The test was successful", response.content)
        self.assertIn(b"live again", response.content)

    def get_user_token(self):
        user = {
            "user": {
                "username": "TestAuthor",
                "email": "test_user@email.com",
                "password": "test123user#Password"
            }
        }

        response = self.client.post(
            reverse('register'), data=user, format='json')
        user = get_user_model()
        user = user.objects.get(username="TestAuthor")
        user.is_active = True
        user.save()
        response.render()
        data = response.content
        token = json.loads(data.decode('utf-8'))['user']['token']
        return token
