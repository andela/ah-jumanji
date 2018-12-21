import logging

import pytest
from django.contrib.auth import get_user_model
from notifications.models import NotificationQuerySet, Notification

from authors.apps.authentication.tests.factories.authentication import \
    UserFactory2
from authors.apps.notifier.utils import Notifier

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestNotifier:

    def test_intersect_querysets(self):
        # add multiple users
        user1 = UserFactory2()
        user2 = UserFactory2()
        user3 = UserFactory2()
        user4 = UserFactory2()

        # get the various query_sets
        user = get_user_model()
        u1 = user.objects.filter(pk=user1.pk)
        u2 = user.objects.filter(pk=user2.pk)
        u3 = user.objects.filter(pk=user3.pk)
        u4 = user.objects.filter(pk=user4.pk)

        users = Notifier.intersect_querysets(u1, u2, u3, u4, u1)
        assert len(users) == 4
        assert Notifier.is_queryset(users) is True

    def test_intersect_queryset_invalid_inputs(self):
        """test queryset intersection with non queryset inputs"""
        with pytest.raises(TypeError):
            Notifier.intersect_querysets("a string")

        user1 = UserFactory2()
        user = get_user_model()
        u1 = user.objects.filter(pk=user1.pk)

        with pytest.raises(TypeError):
            Notifier.intersect_querysets(u1, "a string")

    def test_notify_multiple(self):
        """Test notification of multiple users"""
        user1 = UserFactory2()
        user2 = UserFactory2()
        user3 = UserFactory2()
        user4 = UserFactory2()
        user5 = UserFactory2()

        # get the various query_sets
        user = get_user_model()
        u1 = user.objects.filter(pk=user1.pk)
        u2 = user.objects.filter(pk=user2.pk)
        u3 = user.objects.filter(pk=user3.pk)
        u4 = user.objects.filter(pk=user4.pk)

        # create  Queryset of  4 users
        users = Notifier.intersect_querysets(u1, u2, u3, u4)

        # add notifier
        Notifier.notify_multiple(actor=user5, recipients=users, verb="follows")
        assert len(Notification.objects.all()) > 0

    def test_notify_multiple_with_exceptions(self):
        """Test notification of multiple users with invalid data"""
        user1 = UserFactory2()
        user2 = UserFactory2()
        user3 = UserFactory2()
        user4 = UserFactory2()
        user5 = UserFactory2()

        # get the various query_sets
        user = get_user_model()
        u1 = user.objects.filter(pk=user1.pk)
        u2 = user.objects.filter(pk=user2.pk)
        u3 = user.objects.filter(pk=user3.pk)
        u4 = user.objects.filter(pk=user4.pk)

        # create  Queryset of  4 users
        users = Notifier.intersect_querysets(u1, u2, u3, u4)

        # add notifier
        with pytest.raises(Exception):
            Notifier.notify_multiple(
                actor=user5.username,
                recipients=users,
                verb="follows")

    def test_is_queryset(self):
        user = get_user_model()
        users = user.objects.all()
        assert Notifier.is_queryset(users) is True

    def test_is_queryset_wrong_input(self, test_user):
        with pytest.raises(TypeError):
            user = test_user
            Notifier.is_queryset(user)

    def test_is_user(self, test_user):
        user = test_user
        assert Notifier.is_user(user)

    def test_is_user_for_non_user(self):
        with pytest.raises(TypeError):
            Notifier.is_user("")

    # def test_email_notification(self):
    #     self.fail()
    #
    def test_get_unread_notifications(self, test_user):
        user = test_user
        logger.debug(user)
        notifications = Notifier.get_unread_notifications(user=user)
        logger.debug(notifications)
        assert isinstance(notifications, NotificationQuerySet)
        assert len(notifications) == 0

    def test_get_unread_notifications2(self, test_user, test_user2):
        user = test_user
        user2 = test_user2
        UserFactory2()
        users = get_user_model().objects.all()

        Notifier.notify_multiple(actor=user, recipients=users, verb="some "
                                                                    "action", )

        notifications = Notifier.get_unread_notifications(user=user2)
        logger.debug(notifications)
        assert isinstance(notifications, NotificationQuerySet)
        assert len(notifications) == 1
