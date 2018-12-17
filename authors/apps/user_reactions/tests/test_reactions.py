"""
    Module contains the unittests for the  `user_reactions` app
"""
import json
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

# local imports
# from authors.apps.user_reactions.models import UserReaction
from authors.apps.authentication.models import User
# Create your tests here.


class TestUserReactionModel(APITestCase):
    """
        UNITTESTS for Profile Model
    """

    def setUp(self):
        """
            Set up
        """
        # Generate a test client for sending API requests
        # Define the endpoints for register, login
        self.register_endpoint = reverse('register')
        self.post_article_endpoint = reverse('articles')
        self.reactions_endpoint = reverse('reactions')

        # A sample user to use in the test

        # POSTS articles
        self.user = {
            "user": {
                "username": "username_tu",
                "email": "user@mymail.com",
                "password": "#Strong2-password"
                }
        }
        # reacts
        self.another_user = {
            "user": {
                "username": "dmithamo",
                "email": "dmithamo@mymail.com",
                "password": "#Strong2-password"
                }
        }

        # reacts
        self.third_user = {
            "user": {
                "username": "bmithamo",
                "email": "bmithamo@mymail.com",
                "password": "#Strong2-password"
                }
        }

        # A sample article to use in the tests
        self.article = {
            "title": "Django Unchained",
            "description": "Django without chains",
            "body": "The chains were removed from the Django",
            "author": self.user['user']['username'],
            "tagList": "tag, list"
        }
        self.article_too = {
            "title": "War is not It",
            "description": "Civil War and Stuff",
            "body": "The civil war happened and yes",
            "author": self.another_user['user']['username'],
            "tagList": "civil, war"
        }

        # A sample reaction to use in the tests
        self.reaction = {
            "slug": "django-unchained",
            "reaction": 1
        }

        self.reaction_too = {
            "slug": "war-is-not-it",
            "reaction": -1
        }

        self.fake_reaction = {
            "slug": "war-is-not-it",
            "reaction": 4
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

    def test_user_can_like_an_article(self):
        """
            Test a logged in user can like an existing article
        """
        # Create an article
        self.post_an_article_helper(self.article, self.user)

        # register a user and send a reaction to the article
        user = self.register_user_helper(self.another_user)
        user_token = user['token']

        # Send request to like article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        response = self.client.post(
            self.reactions_endpoint, self.reaction, format='json'
        )

        # extract contents of response
        response_data = json.loads(
            response.content.decode('utf-8'))

        # Assertions
        # Check the status code of the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the contents of the response
        self.assertTrue(response_data["reaction"])
        self.assertEqual(
            response_data["reaction"]["reaction"], self.reaction["reaction"])

    def test_user_can_unlike_a_liked_article(self):
        """
            Test a logged in user can like an existing article
        """
        # Create an article
        self.post_an_article_helper(self.article, self.user)

        # register a user and send a reaction to the article
        user = self.register_user_helper(self.another_user)
        user_token = user['token']

        # Send request to like article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        # LIKE to an article
        self.client.post(
            self.reactions_endpoint, self.reaction, format='json'
        )
        # Send similar request to UNLIKE
        response = self.client.post(
            self.reactions_endpoint, self.reaction, format='json'
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
            "You nolonger `LIKE` this article")

    def test_user_can_not_react_to_non_existent_article(self):
        """
            Test that an error is reported when request is sent to react
            to a non-existent article
        """

        # register a user and send a reaction to the article
        user = self.register_user_helper(self.another_user)
        user_token = user['token']

        # Send request to like article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        response = self.client.post(
            self.reactions_endpoint, self.reaction, format='json'
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
                self.reaction["slug"]))

    def test_user_view_all_reactions_on_all_articles(self):
        """
            Test a logged in user can view all
            reactions on all existing articles
        """
        # Create an article
        self.post_an_article_helper(self.article, self.user)
        # Create another article
        self.post_an_article_helper(self.article_too, self.another_user)

        user = self.register_user_helper(self.third_user)
        user_token = user['token']

        # Send request to like article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        self.client.post(
            self.reactions_endpoint, self.reaction, format='json'
        )
        # Dislike another article
        self.client.post(
            self.reactions_endpoint, self.reaction_too, format='json'
        )

        # Retrieve all reactions
        response = self.client.get(
            self.reactions_endpoint, format='json')

        # extract contents of response
        response_data = json.loads(
            response.content.decode('utf-8'))

        # Assertions
        # Check the status code of the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the contents of the response
        self.assertTrue(response_data["reactions"])
        self.assertEqual(len(response_data["reactions"]), 2)
        self.assertTrue(
            response_data["reactions"][0]["reaction"],
            self.reaction["reaction"])
        self.assertTrue(
            response_data["reactions"][1]["reaction"],
            self.reaction_too["reaction"])

    def test_unlogged_in_user_cannot_react_to_article(self):
        """
            Test that an unlogged in user cannot view the profile
        """
        # Send a GET request to view profile
        response = self.client.post(
            self.reactions_endpoint, self.reaction, format='json'
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
