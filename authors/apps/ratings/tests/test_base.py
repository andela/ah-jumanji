import json

from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from authors.apps.authentication.models import User


class TestBase(APITestCase):
    ''' Base tests class '''

    def setUp(self):

        self.article_author = {
            "user": {
                "username": "author",
                "email": "author@gmail.com",
                "password": "Author@user1"
            }
        }

        self.article_rater = {
            "user": {
                "username": "rater",
                "email": "rater@gmail.com",
                "password": "Rater@user1"
            }
        }

        self.rating = {
            "rating": 5
        }

        self.bad_rating = {
            "rating": 10
        }

        self.article = {
            "title": "Test Post",
            "description": "This is a posting test",
            "body": "The test was successful",
            "tagList": "live again",
            "author": "author"
        }

        # register author and rater and activate them
        self.register_author = self.client.post(
            reverse('register'), data=self.article_author, format='json')
        author = User.objects.get(email='author@gmail.com')
        author.is_active = True
        author.save()

        self.register_rater = self.client.post(
            reverse('register'), data=self.article_rater, format='json')
        rater = User.objects.get(email='rater@gmail.com')
        rater.is_active = True
        rater.save()

        # login author and rater and get their tokens
        self.login_author = self.client.post(
            reverse('login'), data=self.article_author, format='json')
        data = self.login_author.content
        self.author_token = json.loads(data.decode('utf-8'))['user']['token']

        self.login_rater = self.client.post(
            reverse('login'), data=self.article_rater, format='json')
        data = self.login_rater.content
        self.rater_token = json.loads(data.decode('utf-8'))['user']['token']

        # post an article and get slug
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' +
            self.author_token)
        self.post_article = self.client.post(
            reverse('articles'), data=self.article, format='json')
        article = self.post_article.content
        self.slug = json.loads(article.decode('utf-8'))['article'][0]['slug']

        # post a rating and get ID
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.rater_token)
        post_rating = self.client.post(
            reverse(
                'ratings',
                kwargs={
                    "slug": self.slug}),
            data=self.rating,
            format='json')
        rating = post_rating.content
        self.id = json.loads(rating.decode('utf-8'))['rating']['id']
