from rest_framework.test import APITestCase
from django.urls import reverse

from authors.apps.profiles.models import Profile
from authors.apps.articles.models import Articles

# Create your tests here.


class ArticleModelCase(APITestCase):

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

        self.article = Articles(
            slug=self.slug,
            title=self.title,
            description=self.description,
            body=self.body,
            tagList=self.tagList,
            favorited=self.favorited,
            favoritesCount=self.favoritesCount,
            author=Profile.objects.get(
                username=self.author))

    def test_add_article(self):
        original_entries = Articles.objects.count()
        self.article.save()  # Added a value to the db

        new_entries = Articles.objects.count()
        self.assertNotEqual(original_entries, new_entries)

    def test_article_present(self):
        self.article.save()  # Added a value to the db
        self.assertTrue(
            isinstance(
                self.article,
                Articles))  # check if item in the db
