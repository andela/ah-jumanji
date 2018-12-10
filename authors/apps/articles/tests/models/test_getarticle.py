from rest_framework.test import APITestCase
from django.urls import reverse

from authors.apps.authentication.models import User
from authors.apps.articles.models import Articles


class GetArticleTest(APITestCase):

    def register_new_user(self):
        """
            Helper method for registering a user and returning a user
        """

        new_user = {"user": {
            "username": "TestAuthor",
            "email": "testuser@gmail.com",
            "password": "#Password123"
            }
        }

        # Register a user to generate a token
        self.client.post(
            reverse('register'), new_user, format='json')

    def setUp(self):

        self.register_new_user()

        """ Prepares table for tests """
        self.slug = "life_love_death"
        self.title = "Life Love and Death"
        self.description = "What is life?"
        self.body = "This is the real life body."
        self.tagList = "life,love,death"
        self.favorited = True
        self.favoritesCount = 4
        self.author = 'TestAuthor'

        self.slug1 = "life_love_death"
        self.title1 = "Life Love and Death"
        self.description1 = "What is life?"
        self.body1 = "This is the real life body."
        self.tagList1 = "life,love,death"
        self.favorited1 = True
        self.favoritesCount1 = 4
        self.author1 = 'TestAuthor'

        self.article = Articles(
            title=self.title,
            description=self.description,
            body=self.body,
            tagList=self.tagList,
            favorited=self.favorited,
            favoritesCount=self.favoritesCount,
            author=User.objects.get(
                username=self.author))

        self.article1 = Articles(
            title=self.title1,
            description=self.description1,
            body=self.body1,
            tagList=self.tagList1,
            favorited=self.favorited1,
            favoritesCount=self.favoritesCount1,
            author=User.objects.get(
                username=self.author1))

    def test_item_in_db(self):
        '''CONFIRMS IF ITEM IN DB'''
        self.article.save()
        first_count = Articles.objects.count()  # should resolve to 1

        self.article1.save()
        sec_count = Articles.objects.count()  # should resolve to 2

        self.assertEqual(first_count, 1)
        self.assertEqual(sec_count, 2)
        self.assertTrue(sec_count > first_count)
