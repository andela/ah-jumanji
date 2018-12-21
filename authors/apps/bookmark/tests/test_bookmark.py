"""
    Module contains the unittests for the  `bookmark` app
"""
import json
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse

# local imports
from authors.apps.authentication.models import User


class TestBookmarkModel(APITestCase):
    """
        UNITTESTS for  Bookmark Model
    """

    def setUp(self):
        """
            Set up
        """
        # Generate a test client for sending API requests
        # Define the endpoints for register, login
        self.register_endpoint = reverse('register')
        self.post_article_endpoint = reverse('articles')
        self.bookmarks_endpoint = reverse('bookmarks')

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

        # Sample bookmark input data to use in the tests
        self.bookmark = {
            "slug": "django-unchained",
            "bookmark": "True"
        }

        self.bookmark_too = {
            "slug": "war-is-not-it",
            "bookmark": "False"
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

    def test_user_can_bookmark_an_article(self):
        """
            Test a logged in user can like an existing article
        """
        # Create an article
        self.post_an_article_helper(self.article, self.user)

        # register a user and send a bookmark to the article
        user = self.register_user_helper(self.another_user)
        user_token = user['token']

        # Send request to like article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        response = self.client.post(
            self.bookmarks_endpoint, self.bookmark, format='json'
        )

        # extract contents of response
        response_data = json.loads(
            response.content.decode('utf-8'))

        # Assertions
        # Check the status code of the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the contents of the response
        self.assertTrue(response_data["bookmark"])
        self.assertEqual(
            response_data["bookmark"]["bookmark"],
            True)

    def test_user_can_unbookmark_bookmarked_article(self):
        """
            Test a logged in user can like an existing article
        """
        # Create an article
        self.post_an_article_helper(self.article, self.user)

        # register a user and send a bookmark to the article
        user = self.register_user_helper(self.another_user)
        user_token = user['token']

        # Send request to like article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        # LIKE to an article
        self.client.post(
            self.bookmarks_endpoint, self.bookmark, format='json'
        )
        # Send similar request to Bookmark
        response = self.client.post(
            self.bookmarks_endpoint, self.bookmark, format='json'
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
            "You no longer bookmark this article")

    def test_user_can_not_bookmark_non_existent_article(self):
        """
            Test that an error is reported when request is sent to react
            to a non-existent article
        """

        # register a user and send a bookmark to the article
        user = self.register_user_helper(self.another_user)
        user_token = user['token']

        # Send request to like article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        response = self.client.post(
            self.bookmarks_endpoint, self.bookmark, format='json'
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
                self.bookmark["slug"]))

    def test_user_view_all_bookmarks_on_all_articles(self):
        """
            Test a logged in user can view all
            bookmarks on all existing articles
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
            self.bookmarks_endpoint, self.bookmark, format='json'
        )
        # Dislike another article
        self.client.post(
            self.bookmarks_endpoint, self.bookmark_too, format='json'
        )
        # import pdb; pdb.set_trace()
        # Retrieve all BOOKMARKS
        response = self.client.get(
            self.bookmarks_endpoint, format='json')

        # extract contents of response
        response_data = json.loads(
            response.content.decode('utf-8'))

        # Assertions
        # Check the status code of the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the contents of the response
        self.assertTrue(response_data["bookmarks"])
        self.assertEqual(len(response_data["bookmarks"]), 2)
        self.assertTrue(
            response_data["bookmarks"][0]["bookmark"],
            True)
        self.assertFalse(
            response_data["bookmarks"][1]["bookmark"],
            False)

    def test_user_view_bookmarks_on_specific_articles(self):
        """
            Test a logged in user can view
            favourites on a specific existing articles
        """
        # Create an article
        self.post_an_article_helper(self.article, self.user)
        # Create another article
        self.post_an_article_helper(self.article_too, self.another_user)

        user = self.register_user_helper(self.third_user)
        user_token = user['token']

        # Send request to favourite article with auth token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        self.client.post(
            self.bookmarks_endpoint, self.bookmark, format='json'
        )

        url = reverse('article_bookmarks', kwargs={'slug': 'war-is-not-it'})
        response = self.client.get(
            url,
            HTTP_AUTHORIZATION='Token ' + user_token
        )

        # Assertions
        # Check the status code of the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unlogged_in_user_cannot_react_to_article(self):
        """
            Test that an unlogged in user cannot view the profile
        """
        # Send a GET request to view profile
        response = self.client.post(
            self.bookmarks_endpoint, self.bookmark, format='json'
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
