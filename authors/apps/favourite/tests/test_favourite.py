"""
    Module contains the unittests for the  `favourite` app
"""
import json
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

# local imports
from authors.apps.authentication.models import User
from authors.apps.articles.models import Articles


class TestFavouriteModel(APITestCase):
    """
        UNITTESTS for  Favourite Model
    """

    def setUp(self):
        """
            Set up
        """
        # Generate a test client for sending API requests
        # Define the endpoints for register, login
        self.register_endpoint = reverse('register')
        self.post_article_endpoint = reverse('articles')
        self.favourites_endpoint = reverse('favourites')

        # A sample user to use in the test
        self.user = {
            "user": {
                "username": "EmmanuelChayu",
                "email": "emmanuelchayu@andela.com",
                "password": "#1Emmcodes"
            }
        }

        self.another_user = {
            "user": {
                "username": "EmmanuelBeja",
                "email": "beja.emmanuel@gmail.com",
                "password": "#1Emmcodes"
            }
        }

        self.third_user = {
            "user": {
                "username": "Emmbeja",
                "email": "emmcodes@gmail.com",
                "password": "#1Emmcodes"
            }
        }

        # A sample article to use in the tests
        self.article = {
            "title": "Django Unchained",
            "description": "Django without chains",
            "body": "The chains were removed from the Django",
            "tagList": "tag, list"
        }
        self.article_too = {
            "title": "War is not It",
            "description": "Civil War and Stuff",
            "body": "The civil war happened and yes",
            "tagList": "civil, war"
        }

        # Sample favourite input data to use in the tests
        self.favourite = {
            "slug": "django-unchained",
            "favourite": 1
        }

        self.favourite_too = {
            "slug": "war-is-not-it",
            "favourite": -1
        }

        self.fake_favourite = {
            "slug": "war-is-not-it",
            "favourite": 4
        }

    def register_user_helper(self, user_data):
        """
            Helper method for registering a user and returning a user
        """
        # Register a user to generate a token
        register_response = self.client.post(
            self.register_endpoint, user_data, format='json')

        # Activate user account manually
        user = User.objects.get(username=user_data['user']['username'])
        user.is_active = True
        user.save()
        user = User.objects.get(username=user_data['user']['username'])

        # Decode response and extract user
        user = json.loads(
            register_response.content.decode('utf-8'))['user']
        return user

    def post_an_article_helper(self, article, user):
        """
            Helper method for posting an article
        """
        user = self.register_user_helper(user)
        user_token = user['token']

        # Send a POST request to create an article with token
        # Authorize
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)

        # Post an article
        post_article_response = self.client.post(
            self.post_article_endpoint, article, format='json'
        )
        return post_article_response

    def test_user_can_favourite_an_article(self):
        """
            Test a logged in user can favourite an existing article
        """
        # Create an article
        self.post_an_article_helper(self.article, self.user)
        favourite = {
            "slug": Articles.objects.get(title="Django Unchained").slug,
            "favourite": 1
        }
        # register a user and send a favourite to the article
        user = self.register_user_helper(self.another_user)
        user_token = user['token']

        # Send request to favourite article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        response = self.client.post(
            self.favourites_endpoint, favourite, format='json'
        )

        # extract contents of response
        response_data = json.loads(
            response.content.decode('utf-8'))

        # Assertions
        # Check the status code of the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the contents of the response
        self.assertTrue(response_data["favourite"])
        self.assertEqual(
            response_data["favourite"]["favourite"],
            self.favourite["favourite"])

    def test_user_can_unfavourite_a_favourited_article(self):
        """
            Test a logged in user can favourite an existing article
        """
        # Create an article
        self.post_an_article_helper(self.article, self.user)

        favourite = {
            "slug": Articles.objects.get(title="Django Unchained").slug,
            "favourite": 1
        }
        # register a user and send a favourite to the article
        user = self.register_user_helper(self.another_user)
        user_token = user['token']

        # Send request to favourite article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        # Favourite to an article
        self.client.post(
            self.favourites_endpoint, favourite, format='json'
        )
        # Send similar request to Unfavourite
        response = self.client.post(
            self.favourites_endpoint, favourite, format='json'
        )

        # extract contents of response
        response_data = json.loads(
            response.content.decode('utf-8'))

        # Assertions
        # Check the status code of the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the contents of the response
        self.assertEqual(
            response_data['message'],
            "You no longer `FAVOURITE` this article")

    def test_user_can_not_favourite_to_non_existent_article(self):
        """
            Test that an error is reported when request is sent to favourite
            to a non-existent article
        """

        # register a user and send a favourite to the article
        user = self.register_user_helper(self.another_user)
        user_token = user['token']

        # Send request to favourite article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        response = self.client.post(
            self.favourites_endpoint, self.favourite, format='json'
        )

        # extract contents of response
        response_data = json.loads(
            response.content.decode('utf-8'))

        # Assertions
        # Check the status code of the response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Check the contents of the response
        self.assertEqual(
            response_data["detail"],
            "Article with slug `{}` does not exist".format(
                self.favourite["slug"]))

    def test_user_view_all_favourites_on_all_articles(self):
        """
            Test a logged in user can view all
            favourites on all existing articles
        """
        # Create an article
        self.post_an_article_helper(self.article, self.user)

        favourite = {
            "slug": Articles.objects.get(title="Django Unchained").slug,
            "favourite": 1
        }
        # Create another article
        self.post_an_article_helper(self.article_too, self.another_user)

        favourite_too = {
            "slug": Articles.objects.get(title="War is not It").slug,
            "favourite": 1
        }
        user = self.register_user_helper(self.third_user)
        user_token = user['token']

        # Send request to favourite article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        self.client.post(
            self.favourites_endpoint, favourite, format='json'
        )
        # Unfavourite another article
        self.client.post(
            self.favourites_endpoint, favourite_too, format='json'
        )
        # Retrieve all FAVOURITES
        response = self.client.get(
            self.favourites_endpoint, format='json')

        # extract contents of response
        response_data = json.loads(
            response.content.decode('utf-8'))

        # Assertions
        # Check the status code of the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the contents of the response
        self.assertTrue(response_data["favourites"])
        self.assertEqual(len(response_data["favourites"]), 2)
        self.assertTrue(
            response_data["favourites"][0]["favourite"],
            favourite["favourite"])
        self.assertTrue(
            response_data["favourites"][1]["favourite"],
            favourite_too["favourite"])

    def test_user_view_favourites_on_specific_articles(self):
        """
            Test a logged in user can view
            favourites on a specific existing articles
        """
        # Create an article
        self.post_an_article_helper(self.article, self.user)

        favourite = {
            "slug": Articles.objects.get(title="Django Unchained").slug,
            "favourite": 1
        }
        # Create another article
        self.post_an_article_helper(self.article_too, self.another_user)

        user = self.register_user_helper(self.third_user)
        user_token = user['token']

        # Send request to favourite article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        self.client.post(
            self.favourites_endpoint, favourite, format='json'
        )

        url = reverse('article_favourites',
                      kwargs={'slug':
                              Articles.objects.get(
                                  title="War is not It").slug})
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION='Token ' + user_token
        )

        # Assertions
        # Check the status code of the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unlogged_in_user_cannot_favourite_to_article(self):
        """
            Test that an unlogged in user cannot view the profile
        """
        # Send a GET request to view profile
        response = self.client.post(
            self.favourites_endpoint, self.favourite, format='json'
        )

        # extract contents of response
        response_data = json.loads(
            response.content.decode('utf-8'))

        response_message = response_data['detail']

        # Assertions
        # assert that the response message is as below
        self.assertEqual(
            response_message, "Authentication credentials were not provided.")

        # Check that the reponse status code is 401
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED)
