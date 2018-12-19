import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User


class TestShareEndpoint(APITestCase):

    def setUp(self):

        self.token = self.get_user_token()

        self.data = {
            "slug": "posting_test",
            "title": "Posting Test",
            "description": "this is a posting test",
            "body": "The test was successful",
            "tagList": "live again",
            "author": "TestAuthor"
        }
        self.all_setup()

    def test_get_facebook_link(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articleSpecific', kwargs={'slug': 'life-love-death'})
        self.client.post(url, self.data, format='json')
        link_url = reverse(
                            'share_article',
                            kwargs={
                                    'slug': 'life-love-death',
                                    'provider': 'facebook'})
        response = self.client.get(link_url, format='json')
        self.assertEqual(response.data['provider'], 'facebook')

    def test_get_twitter_link(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articleSpecific', kwargs={'slug': 'life-love-death'})
        self.client.post(url, self.data, format='json')
        link_url = reverse(
                            'share_article',
                            kwargs={
                                    'slug': 'life-love-death',
                                    'provider': 'twitter'})
        response = self.client.get(link_url, format='json')
        self.assertEqual(response.data['provider'], 'twitter')

    def test_get_email_link(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articleSpecific', kwargs={'slug': 'life-love-death'})
        self.client.post(url, self.data, format='json')
        link_url = reverse(
                            'share_article',
                            kwargs={
                                    'slug': 'life-love-death',
                                    'provider': 'email'})
        response = self.client.get(link_url, format='json')
        self.assertEqual(response.data['provider'], 'email')

    def test_using_unexisting_article_slug(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articleSpecific', kwargs={'slug': 'life-love-death'})
        self.client.post(url, self.data, format='json')
        link_url = reverse(
                            'share_article',
                            kwargs={
                                    'slug': 'life-love',
                                    'provider': 'email'})
        response = self.client.get(link_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Article does not exist')

    def test_using_invalid_provider(self):

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articleSpecific', kwargs={'slug': 'life-love-death'})
        self.client.post(url, self.data, format='json')
        link_url = reverse(
                            'share_article',
                            kwargs={
                                    'slug': 'life-love-death',
                                    'provider': 'reddit'})
        response = self.client.get(link_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'provider link is invalid')

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
            author=User.objects.get(username=self.author))

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
