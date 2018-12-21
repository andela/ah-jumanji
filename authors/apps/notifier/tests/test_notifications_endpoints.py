import logging

import pytest
from notifications.models import Notification
from rest_framework import status
from rest_framework.reverse import reverse

from authors.apps.authentication.tests.factories.authentication import \
    ArticlesFactory, MailingListFactory, ProfileFactory, FavouritesFactory, \
    CommentFactory
from authors.apps.core.factories.authentication import FollowerFactory

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestNotifications:
    def test_get_unread_notifications_none(self, test_auth_client):
        """test get notifications with empty results set"""
        response = test_auth_client.get(reverse('notifications'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data[
                   'message'] == "You have no notifications to display"

    def test_get_unread_notifications_with_results(self, test_auth_client,
                                                   test_user, test_user2):
        """Test the endpoint when notifications are present"""
        # get user instances
        user = test_user
        user2 = test_user2

        # add the users to the mailing list
        MailingListFactory(
            user=user,
            email_notifications=True,
            push_notifications=True
        )
        MailingListFactory(
            user=test_user2,
            email_notifications=True,
            push_notifications=True
        )

        # create a follower relationship
        FollowerFactory(followed=user2, follower=user)

        # create an article for user2 and user
        article1 = ArticlesFactory(author=user)
        article2 = ArticlesFactory(author=user2)

        # favourite the article
        profile1 = ProfileFactory(user=user)
        profile2 = ProfileFactory(user=user2)

        FavouritesFactory(user=profile1, article=article2, favourite=1)
        FavouritesFactory(user=profile2, article=article1, favourite=1)

        # comment on the article
        CommentFactory(article=article1, commenter=profile2)
        CommentFactory(article=article2, commenter=profile1)

        response = test_auth_client.get(reverse('notifications'))
        logger.error(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data

        logger.error(response.data)
        assert response.data['count'] >= 3

    def test_get_read_notification(self, test_user2, test_user,
                                   test_auth_client):
        """Test the endpoint when notifications are present"""
        # get user instances
        user = test_user
        user2 = test_user2

        # add the users to the mailing list
        MailingListFactory(
            user=user,
            email_notifications=True,
            push_notifications=True
        )
        MailingListFactory(
            user=test_user2,
            email_notifications=True,
            push_notifications=True
        )

        # create a follower relationship
        FollowerFactory(followed=user2, follower=user)

        # create an article for user2
        ArticlesFactory(author=user2)

        notification = Notification.objects.all()[0]

        response = test_auth_client.get(
            reverse('read-notification', args=[notification.pk])
        )

        notification = Notification.objects.all()[0]

        assert response.status_code == status.HTTP_200_OK
        assert notification.unread is False

    def test_mark_read_notification_as_unread(self, test_auth_client,
                                              test_user,
                                              test_user2):
        # get user instances
        user = test_user
        user2 = test_user2

        # add the users to the mailing list
        MailingListFactory(
            user=user,
            email_notifications=True,
            push_notifications=True
        )
        MailingListFactory(
            user=test_user2,
            email_notifications=True,
            push_notifications=True
        )

        # create a follower relationship
        FollowerFactory(followed=user2, follower=user)

        # create an article for user2
        ArticlesFactory(author=user2)
        notification = Notification.objects.all()[0]

        # read the notification
        test_auth_client.get(
            reverse('read-notification', args=[notification.pk])
        )
        # mark notification as unread
        response = test_auth_client.get(
            reverse('mark-notification-read', args=[notification.pk])
        )
        notification = Notification.objects.all()[0]

        assert response.status_code == status.HTTP_200_OK
        assert notification.unread is True

    def test_mark_all_unread_read(self, test_auth_client, test_user,
                                  test_user2):
        user = test_user
        user2 = test_user2

        # add the users to the mailing list
        MailingListFactory(
            user=user,
            email_notifications=True,
            push_notifications=True
        )
        MailingListFactory(
            user=test_user2,
            email_notifications=True,
            push_notifications=True
        )

        # create a follower relationship
        FollowerFactory(followed=user2, follower=user)

        # create an article for user2
        ArticlesFactory(author=user2)

        test_auth_client.get(reverse('mark-notifications-read'))
        response = test_auth_client.get(reverse('notifications'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data[
                   'message'] == "You have no notifications to display"

    def test_get_all_marked_as_read(self, test_auth_client, test_user,
                                    test_user2):
        user = test_user
        user2 = test_user2

        # add the users to the mailing list
        MailingListFactory(
            user=user,
            email_notifications=True,
            push_notifications=True
        )
        MailingListFactory(
            user=test_user2,
            email_notifications=True,
            push_notifications=True
        )

        # create a follower relationship
        FollowerFactory(followed=user2, follower=user)

        # create an article for user2
        ArticlesFactory(author=user2)

        test_auth_client.get(reverse('mark-notifications-read'))
        response = test_auth_client.get(
            reverse('marked-as-read-notifications'))

        assert response.status_code == status.HTTP_200_OK
        assert 'notifications' in response.data
        assert response.data['notifications'][0]['unread'] is False
