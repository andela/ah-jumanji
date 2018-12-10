import json

from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User


class TestGetEndpoint(APITestCase):

    def setUp(self):
        """ Prepares table for tests """
        self.token = self.get_user_token()

        self.slug = "life_love_death"
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
            author=User.objects.get(username=self.author))
        self.article.save()

    def test_getArticle_status(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test for specific article calls

    def test_getArticle_content(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articles')
        response = self.client.get(url)

        response.render()
        self.assertIn(b"life_love_death", response.content)
        self.assertIn(b"Life Love and Death", response.content)
        self.assertIn(b"What is life?", response.content)
        self.assertIn(b"This is the real life body.", response.content)
        self.assertIn(b"[\"life\",\"love\",\"death\"]", response.content)
        self.assertIn(b"4", response.content)

    def test_get_specific_article(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articleSpecific', kwargs={'slug': 'life_love_death'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response.render()
        self.assertIn(b"life_love_death", response.content)
        self.assertIn(b"Life Love and Death", response.content)
        self.assertIn(b"What is life?", response.content)
        self.assertIn(b"This is the real life body.", response.content)
        self.assertIn(b"[\"life\",\"love\",\"death\"]", response.content)
        self.assertIn(b"4", response.content)

    def test_wrong_request(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse(
            'articleSpecific', kwargs={
                'slug': 'life_love_death_live'})
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response.render()
        self.assertIn(b"Article does not exist", response.content)

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
