"""
    Module contains the unittests for the  `profiles` app
"""
import json
from rest_framework.test import APITestCase
from django.urls import reverse

# local imports
from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User
# Create your tests here.


class TestProfileModel(APITestCase):
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
        self.login_endpoint = reverse('login')
        self.profile_endpoint = reverse('user_profiles')

        self.user = {"user": {
            "username": "rkemmy69",
            "email": "rkemmy69@mymail.com",
            "password": "#Strong2-password"
        }
        }

    def register_user_helper(self):
        """
            Helper method for registering a user and returning a user
        """
        # Register a user to generate a token
        register_response = self.client.post(
            self.register_endpoint, self.user, format='json')
        # Activate user account manually
        user = User.objects.get(username=self.user['user']['username'])
        user.is_active = True
        user.save()
        user = User.objects.get(username=self.user['user']['username'])

        # Decode response and extract user
        user = json.loads(
            register_response.content.decode('utf-8'))['user']

        return user

    def test_profile_auto_created_on_user_creation(self):
        """
            Test autocreation of profile for each user
        """
        # profile counts before user is saved
        prof_count_before = Profile.objects.count()

        # Register a user and recount profiles
        self.client.post(
            self.register_endpoint, self.user, format='json')

        prof_count_after = Profile.objects.count()

        # assertions
        self.assertEqual(prof_count_after - prof_count_before, 1)

    def test_unlogged_in_user_cannot_view_profile(self):
        """
            Test that an unlogged in user cannot view the profile
        """
        # Send a GET request to view profile
        view_profile_response = self.client.get(
            self.profile_endpoint, format='json')

        # extract status code from response
        response_message = json.loads(
            view_profile_response.content.decode('utf-8'))['detail']

        # Assertions
        # assert that the response message is as below
        self.assertEqual(
            response_message, "Authentication credentials were not provided.")

        # Check that the reponse status code is 401
        self.assertEqual(view_profile_response.status_code, 401)

    def test_user_can_view_profile(self):
        """
            Test that a logged in user can view the profile
        """
        # Register a user to generate a token
        # Decode response and extract token
        user = self.register_user_helper()
        user_token = user['token']

        # Send a GET request to view profile with token
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        view_profile_response = self.client.get(
            self.profile_endpoint, format='json')

        # extract profile from response
        user_profile = json.loads(
            view_profile_response.content.decode('utf-8'))['profile']

        # Assertions
        # assert that the user_profile is not null
        self.assertTrue(user_profile)

        # assert that the user_profile is not null
        self.assertEqual(view_profile_response.status_code, 200)

        # assert that profile contains username of signed in user
        self.assertEqual(
            user_profile['username'], user['username']
        )

    def test_user_can_update_profile(self):
        """
            Test that a logged in user can view the profile
        """
        # Register a user to generate a token
        # Decode response and extract token
        user = self.register_user_helper()
        user_token = user['token']

        # Send a PUT request to update profile with token
        changes_to_profile = {
            "profile": {
                "country": "USB",
                "twitter_handle": "@dmithamo2"
            }
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
        view_profile_response = self.client.put(
            self.profile_endpoint, data=changes_to_profile, format='json')

        # extract profile from response
        user_profile = json.loads(
            view_profile_response.content.decode('utf-8'))['profile']

        # Assertions
        # assert that the status_code is 200 OK
        self.assertEqual(view_profile_response.status_code, 200)

        # assert that profile contains username of signed in user
        self.assertEqual(
            user_profile['country'], changes_to_profile['profile']['country'])

        # assert that twitter_handle changes as expected
        self.assertEqual(
            user_profile['twitter_handle'],
            changes_to_profile['profile']['twitter_handle'])
