import os
import pytest
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status


@pytest.mark.skip(reason="Social auth token already expired")
class SocialOauthTest(APITestCase):
    """
    Test user social login
    """
    FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    GOOGLE_ACCESS_TOKEN = "Time bound"

    def setUp(self):
        self.facebook_data = {
            "provider": "facebook",
            "access_token": self.FACEBOOK_ACCESS_TOKEN
        }

        self.twitter_data = {
            "provider": "twitter",
            "access_token": self.TWITTER_ACCESS_TOKEN,
            "access_token_secret": self.TWITTER_ACCESS_TOKEN_SECRET
        }

    def test_facebook_login(self):
        """ Test successful user login """
        response = self.client.post(reverse('social_auth'),
                                    self.facebook_data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response.render()
        self.assertIn(b"GransonOyombe",
                      response.content)  # TEST FOR USERNAME
        self.assertIn(b"facebook", response.content)  # TEST FOR THE PROVIDER
        self.assertIn(b"social_token", response.content)  # TEST FOR THE TOKEN

    def test_facebook_login_errors(self):
        """ Test wrong access token """
        facebook_wrong_token = {
            "provider": "facebook",
            "access_token": "wrong-{}".format(self.FACEBOOK_ACCESS_TOKEN)
        }
        response = self.client.post(reverse('social_auth'),
                                    facebook_wrong_token,
                                    format='json')
        self.assertIn(b"access_token/token_secret error",
                      response.content)  # wrong credentials passed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test wrong provider
        facebook_wrong_provider = {
            "provider": "face",
            "access_token": self.FACEBOOK_ACCESS_TOKEN
        }
        response = self.client.post(reverse('social_auth'),
                                    facebook_wrong_provider,
                                    format='json')
        self.assertIn(b"Provider is invalid",
                      response.content)  # wrong credentials passed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_twitter_login(self):
        """ Test successful user login """
        response = self.client.post(reverse('social_auth'),
                                    self.twitter_data,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response.render()
        self.assertIn(b"GransonO",
                      response.content)  # TEST FOR USERNAME
        self.assertIn(b"twitter", response.content)  # TEST FOR THE PROVIDER
        self.assertIn(b"social_token", response.content)  # TEST FOR THE TOKEN

    def test_twitter_login_errors(self):
        # Test wrong access token
        facebook_wrong_token = {
            "provider": "facebook",
            "access_token": "wrong-{}".format(self.FACEBOOK_ACCESS_TOKEN)
        }
        response = self.client.post(reverse('social_auth'),
                                    facebook_wrong_token,
                                    format='json')
        self.assertIn(b"access_token/token_secret error",
                      response.content)  # wrong credentials passed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test wrong provider
        twitter_wrong_provider = {
            "provider": "face",
            "access_token": "This is a wrong token",
            "access_token_secret": self.TWITTER_ACCESS_TOKEN_SECRET
        }
        response = self.client.post(reverse('social_auth'),
                                    twitter_wrong_provider,
                                    format='json')
        self.assertIn(b"Provider is invalid",
                      response.content)  # wrong credentials passed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_google_login(self):
        pass

    def test_google_login_errors(self):
        pass
