from rest_framework.test import APITestCase
from django.urls import reverse

from authors.apps.profiles.models import Profile
from authors.apps.articles.models import Articles


class DeleteArticleTest(APITestCase):

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
        """ Prepares table for tests """

        self.register_new_user()

        # first Item
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

        # Second Item
        self.slug1 = "life_love_death1"
        self.title1 = "Life Love and Death1"
        self.description1 = "What is life1?"
        self.body1 = "This is the real life body.1"
        self.tagList1 = "life,love,death1"
        self.favorited1 = True
        self.favoritesCount1 = 4
        self.author1 = 'TestAuthor'

        self.article1 = Articles(
            slug=self.slug1,
            title=self.title1,
            description=self.description1,
            body=self.body1,
            tagList=self.tagList1,
            favorited=self.favorited1,
            favoritesCount=self.favoritesCount1,
            author=Profile.objects.get(
                username=self.author1))

        # Two objects added to db
        self.article.save()
        self.article1.save()

    def test_delete_item(self):
        '''Deletes item from DB'''
        # get initial total objects
        total_objects = Articles.objects.count()
        print(total_objects)
        self.assertTrue(total_objects == 2)

        # deletes an item from the db
        delete_object = Articles.objects.get(slug='life_love_death')
        delete_object.delete()

        # get final total objects
        total_objects = Articles.objects.count()
        print(total_objects)
        self.assertTrue(total_objects == 1)
