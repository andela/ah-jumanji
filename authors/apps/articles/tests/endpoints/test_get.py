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

    def test_get_all_articles(self):
        """
        This tests getting all articles successfully
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_successfully_not_getting_articles_if_token_not_used(self):
        """
        Unauthorized error returned if no token is passed in
        """
        url = reverse('articles')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_article_id(self):
        """
        Tests the pk of the article is true
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articles')
        response = self.client.get(url)
        self.assertIn(b"1", response.content)

    def test_articles_are_paginated(self):
        """
        This tests if the returned articles are paginated
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articles')
        response = self.client.get(url).render()
        # this checks the number of articles in the database
        self.assertIn(b"1", response.content)
        # next is null since there is only one article posted
        self.assertIn(b"null", response.content)
        # previous is null since only one article has been posted
        # the page_size holds ten articles per page
        self.assertIn(b"null", response.content)  # previous

    def test_get_specific_article(self):
        """
        This gets a specific article
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articleSpecific', kwargs={'slug': 'life_love_death'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_getting_and_checking_articles_content(self):
        """
        This checks if the right content of an article is returned
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('articles')
        response = self.client.get(url).render()
        # checks if the body passed during posting is the one returned
        self.assertIn(b"This is the real life body.", response.content)

        # checks if favoritesCount returned is 4
        self.assertIn(b"4", response.content)

    def test_wrong_request(self):
        """
        Checks request for a non existing article
        """
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
