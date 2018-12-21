import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from authors.apps.articles.models import Articles
from authors.apps.profiles.models import Profile


class TestGetEndpoint(APITestCase):

    def setUp(self):

        self.token = self.get_user_token()

        self.slug = "life-love-death"
        self.title = "Life Love and Death"
        self.description = "What is life?"
        self.body = "This is the real life body."
        self.tagList = "life,love,death"
        self.author = 'TestAuthor'

        self.article = Articles(
            slug=self.slug,
            title=self.title,
            description=self.description,
            body=self.body,
            tagList=self.tagList,
            author=Profile.objects.get(username=self.author))
        self.article.save()

    def test_delArticle_status(self):
        url = reverse('articleSpecific', kwargs={'slug': 'life-love-death'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.delete(url)
        response.render()
        self.assertIn(
            b'Article life-love-death deleted successfully',
            response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_status(self):
        url = reverse('articleSpecific', kwargs={'slug': 'life-love'})
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.delete(url)
        response.render()
        self.assertIn(b'Could not find that article', response.content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
        # Token returned after login
