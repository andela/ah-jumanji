import logging

import pytest
from rest_framework.reverse import reverse

from authors.apps.authentication.tests.factories.authentication import \
    ProfileFactory

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestFollowerSystem:

    def test_get_user_profile(self, test_user, test_auth_client, test_profile):
        profile = test_profile
        logger.debug(profile)
        response = test_auth_client.get(
            reverse('profile-details', args=[test_user.username]))
        assert response.status_code == 200
        assert 'following' in response.data
        logger.error(response.data)
        assert response.data['user'] == test_user.username
        assert isinstance(response.data['following'], bool)

    def test_check_if_following(self, test_auth_client,
                                test_following_relation):
        relationship = test_following_relation
        user = relationship.followed
        ProfileFactory(user=user)
        ProfileFactory(user=relationship.follower)
        response = test_auth_client.get(reverse('profile-details',
                                                args=[user.username]
                                                )
                                        )
        logger.debug(response.data)
        assert response.data['following'] is True

    def test_get_user_profile_wrong_username(self, test_user, test_auth_client,
                                             test_profile):
        profile = test_profile
        logger.debug(profile)
        response = test_auth_client.get(
            reverse('profile-details', args=["random_username"]))
        assert response.status_code == 404

    def test_follow_user(self, test_auth_client,
                         test_profile, test_profile2):
        profile1 = test_profile
        logger.debug(profile1)
        profile2 = test_profile2
        username = profile2.user.username

        response = test_auth_client.post(reverse('follow', args=[username]))
        logger.debug(response.data)
        assert response.status_code == 200
        assert 'message' in response.data
        assert 'relationship' in response.data

    def test_follow_unknown_user(self, test_auth_client,
                                 test_profile, test_profile2):
        profile1 = test_profile
        profile2 = test_profile2

        logger.debug(profile1)
        logger.debug(profile2)

        response = test_auth_client.post(reverse('follow', args=["unknown"]))
        logger.debug(response.data)
        assert response.status_code == 404
        assert 'detail' in response.data
        assert response.data['detail'] == "The user specified" \
                                          " was not found"

    def test_follow_already_followed_user(self, test_auth_client,
                                          test_profile, test_profile2):
        profile1 = test_profile
        logger.debug(profile1)
        profile2 = test_profile2
        username = profile2.user.username

        response = test_auth_client.post(reverse('follow', args=[username]))
        logger.debug(response)
        response2 = test_auth_client.post(reverse('follow', args=[username]))

        assert response2.status_code == 403
        assert 'message' in response2.data
        assert response2.data['message'] == " You are already" \
                                            " following %s" % username

    def test_unfollow_unfollowed_user(self, test_auth_client, test_profile,
                                      test_profile2):
        profile1 = test_profile
        profile2 = test_profile2
        username = profile2.user.username

        logger.debug(profile1)

        response = test_auth_client.delete(reverse('follow', args=[username]))
        assert response.status_code == 403
        assert response.data['message'] == " You are not " \
                                           "currently following %s" % username

    def test_unfollow_user(self, test_auth_client, test_following_relation):
        relationship = test_following_relation
        user2 = relationship.followed

        response = test_auth_client.delete(
            reverse('follow', args=[user2.username]))
        assert response.status_code == 200
        assert 'message' in response.data

    def test_unfollow_unknown_user(self, test_auth_client):
        response = test_auth_client.delete(reverse('follow', args=["unknown"]))
        assert response.status_code == 404

    def test_unauthorised_user(self, test_client):
        response = test_client.post(reverse('follow', args=["unknown"]))
        assert response.status_code == 401

    def test_get_all_followers_no_followers(self, test_auth_client):
        response = test_auth_client.get(reverse('followers'))
        logger.debug(response.data)
        assert response.status_code == 200
        assert "message" in response.data
        assert response.data["message"] == 'You currently have ' \
                                           'no followers to display'

    def test_get_all_followers_no_followed(self, test_auth_client):
        response = test_auth_client.get(reverse('followed'))
        logger.debug(response.data)
        assert response.status_code == 200
        assert "message" in response.data
        assert response.data["message"] == 'You are not currently' \
                                           ' following other users'

    def test_get_all_followed(self, test_auth_client, test_following_relation):
        relationship = test_following_relation
        logger.debug(relationship)

        response = test_auth_client.get(reverse('followed'))
        logger.debug(response.data)
        assert response.status_code == 200
        assert "message" in response.data
        assert response.data["message"] == 'You are currently' \
                                           ' following 1 users'

    def test_get_all_following(self, test_auth_client,
                               test_reversed_following_relation):
        relationship = test_reversed_following_relation
        logger.debug(relationship)
        response = test_auth_client.get(reverse('followers'))
        logger.debug(response.data)
        assert response.status_code == 200
        assert "message" in response.data
        assert response.data["message"] == 'You have 1 followers'
