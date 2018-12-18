"""
    Module contains the unittests for the  `user_reactions` app
"""
import json
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

# local imports
from authors.apps.authentication.models import User
from authors.apps.articles.models import Articles
from authors.apps.comments.models import Comment
# Create your tests here.


class TestUserReactionOnCommentModel(APITestCase):
    """
        UNITTESTS for User Reactions on Comments
    """

    def setUp(self):
        """
            Set up
        """
        # Generate a test client for sending API requests
        # Define the endpoints for register
        self.register_endpoint = reverse('register')
        self.login_endpoint = reverse('login')
        self.comment_reactions_endpoint = reverse('comment_reactions')

        # A sample user to use in the test

        # POSTS articles and comments
        self.user = {
            "user": {
                "username": "username_tu",
                "email": "user@mymail.com",
                "password": "#Strong2-password"
                }
        }
        # reacts to comment
        self.another_user = {
            "user": {
                "username": "dmithamo",
                "email": "dmithamo@mymail.com",
                "password": "#Strong2-password"
                }
        }

        # reacts to comments
        self.third_user = {
            "user": {
                "username": "lkhalegi",
                "email": "lkhalegi@me.com",
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
        self.article_two = {
            "title": "War is not It",
            "description": "Civil War and Stuff",
            "body": "The civil war happened and yes",
            "author": self.another_user['user']['username'],
            "tagList": "civil, war"
        }

        # comments for use in tests
        self.comment_one = {
            "body": "Mike will made it"
        }
        self.comment_two = {
            "body": "Mithamo made a comment. Or did he?"
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

    def post_an_article_and_comment_helper(self, article):
        """
            Helper method for posting an article
        """
        # Insert an article into the db manually
        # Register user first
        self.register_user_helper(self.user)
        user = User.objects.get(username=self.user['user']['username'])

        # Insert an article into the db
        Articles.objects.create(
            title=article['title'],
            body=article['body'],
            author=user
        )
        # Insert a comment into the db
        # Needs an article
        article = Articles.objects.get(title=article['title'])
        Comment.objects.create(
            article=article,
            body=self.comment_one['body'],
            commenter_id=user.id
        )
        # Insert another comment
        Comment.objects.create(
            article=article,
            body=self.comment_two['body'],
            commenter_id=user.id
        )

    def test_logged_in_user_can_like_a_comment(self):
        """
            Test a logged in user can like an existing comment
        """
        # Create an article, and add a comment
        self.post_an_article_and_comment_helper(self.article)

        # login a user and send a reaction to the article
        user = self.register_user_helper(self.another_user)
        user_token = user['token']

        # Configure reaction
        # Extract comment_id from db
        comment_one = Comment.objects.get(body=self.comment_one['body'])

        reaction = {
            "comment_id": comment_one.id,
            "reaction": 1
        }

        # Send request to like comment with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        response = self.client.post(
            self.comment_reactions_endpoint, reaction, format='json'
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
            response_data["reaction"]["reaction"], reaction["reaction"])

    def test_user_can_unlike_a_liked_comment(self):
        """
            Test a logged in user can unlike a liked comment
        """
        # Create an article, and add a comment
        self.post_an_article_and_comment_helper(self.article_two)

        # login a user and send a reaction to the article
        user = self.register_user_helper(self.another_user)
        user_token = user['token']

        # Configure reaction
        # Extract comment_id from db
        comment_two = Comment.objects.get(body=self.comment_one['body'])

        reaction = {
            "comment_id": comment_two.id,
            "reaction": -1
        }

        # Send request to like comment with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        self.client.post(
            self.comment_reactions_endpoint, reaction, format='json'
        )
        response = self.client.post(
            self.comment_reactions_endpoint, reaction, format='json'
        )

        # extract contents of response
        response_data = json.loads(
            response.content.decode('utf-8'))

        # Assertions
        # Check the status code of the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the contents of the response
        self.assertEqual(
            response_data["message"],
            'You nolonger `DISLIKE` this comment')

    def test_user_can_only_like_or_unlike(self):
        """
            Test response when user sends an invalid reaction
        """
        # Create an article, and add a comment
        self.post_an_article_and_comment_helper(self.article)

        # login a user and send a reaction to the article
        user = self.register_user_helper(self.another_user)
        user_token = user['token']

        # Configure reaction
        # Extract comment_id from db
        comment_one = Comment.objects.get(body=self.comment_one['body'])

        reaction = {
            "comment_id": comment_one.id,
            "reaction": 10
        }

        # Send request to like comment with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        response = self.client.post(
            self.comment_reactions_endpoint, reaction, format='json'
        )

        # extract contents of response
        response_data = json.loads(
            response.content.decode('utf-8'))

        # Assertions
        # Check the status code of the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check the contents of the response
        self.assertEqual(
            response_data['errors']['reaction'],
            ['"{}" is not a valid choice.'.format(reaction['reaction'])]
        )

    def test_user_can_not_react_to_non_existent_comment(self):
        """
            Test that an error is reported when request is sent to react
            to a non-existent article
        """

        # register a user and send a reaction to the article
        user = self.register_user_helper(self.another_user)
        user_token = user['token']

        # Fake reaction
        fake_comment_reaction = {
            "comment_id": 100000,
            "reaction": -1
        }

        # Send request to like article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        response = self.client.post(
            self.comment_reactions_endpoint,
            fake_comment_reaction, format='json'
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
            'Comment with id `{}` does not exist'.format(
                fake_comment_reaction["comment_id"]))

    def test_user_view_all_reactions_on_all_comments(self):
        """
            Test a logged in user can view all
            reactions on all existing comments
        """
        # Create an article and comment
        self.post_an_article_and_comment_helper(self.article)

        user = self.register_user_helper(self.third_user)
        user_token = user['token']

        # Configure reaction
        # Extract comment_id from db
        comment_one = Comment.objects.get(body=self.comment_one['body'])
        comment_two = Comment.objects.get(body=self.comment_two['body'])

        reaction_one = {
            "comment_id": comment_one.id,
            "reaction": -1
        }

        reaction_two = {
            "comment_id": comment_two.id,
            "reaction": -1
        }

        # Send request to like comment with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        # React to a comment
        self.client.post(
            self.comment_reactions_endpoint, reaction_one, format='json'
        )
        # React to another comment
        self.client.post(
            self.comment_reactions_endpoint, reaction_two, format='json'
        )

        # Retrieve all reactions
        response = self.client.get(
            self.comment_reactions_endpoint, format='json')

        # extract contents of response
        response_data = json.loads(
            response.content.decode('utf-8'))

        # Assertions
        # Check the status code of the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the contents of the response
        self.assertEqual(type(response_data["reactions"]), list)
        self.assertTrue(
            response_data["reactions"][0]["reaction"],
            reaction_one["reaction"])
        self.assertTrue(
            response_data["reactions"][1]["reaction"],
            reaction_two["reaction"])

    def test_unlogged_in_user_cannot_react_to_article(self):
        """
            Test that an unlogged in user cannot view the profile
        """
        # Create an article, and add a comment
        self.post_an_article_and_comment_helper(self.article_two)

        # Configure reaction
        # Extract comment_id from db
        comment_two = Comment.objects.get(body=self.comment_one['body'])

        reaction = {
            "comment_id": comment_two.id,
            "reaction": -1
        }

        # Send request to unlike comment without auth token
        response = self.client.post(
            self.comment_reactions_endpoint, reaction, format='json'
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
