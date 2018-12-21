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

        self.data = {
            "slug": "posting_test",
            "title": "Posting Test",
            "description": "this is a posting test",
            "body": "The test was successful",
            "tagList": "live again"
        }
        self.all_setup()

    def test_putArticle_status(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articleSpecific', kwargs={'slug': 'life-love-death'})
        response = self.client.put(url, self.data, format='json')
        response.render()
        self.assertIn(b'Update successful', response.content)

    def test_putArticle_no_token_provided(self):
        url = reverse('articleSpecific', kwargs={'slug': 'life-love-death'})
        response = self.client.put(url, self.data, format='json')
        response.render()
        self.assertIn(
                        b'Authentication credentials were not provided.',
                        response.content)

    def test_get_specific_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articleSpecific', kwargs={'slug': 'life-love-death'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response.render()
        self.assertIn(b"life-love-death", response.content)
        self.assertIn(b"Life Love and Death", response.content)
        self.assertIn(b"What is life?", response.content)
        self.assertIn(b"This is the real life body.", response.content)
        self.assertIn(b"life,love,death", response.content)
        self.assertIn(b"4", response.content)

    def all_setup(self):

        self.slug = "life-love-death"
        self.title = "Life Love and Death"
        self.description = "What is life?"
        self.body = "This is the real life body."
        self.tagList = "life,love,death"
        self.favorited = True
        self.favoritesCount = 4
        self.author = 'TestAuthor'

        self.article = Articles(
            slug=self.slug,
            title=self.title,
            description=self.description,
            body=self.body,
            tagList=self.tagList,
            favorited=self.favorited,
            favoritesCount=self.favoritesCount,
            author=Profile.objects.get(username=self.author))

        self.article.save()

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
