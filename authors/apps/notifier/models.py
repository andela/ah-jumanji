from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.

class MailingList(models.Model):
    """A table containing users who receive email notifier"""
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             )
    # The status of the user with regards to receiving notifier
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)

    def is_email_subscribed(user):
        """
        Verify that a user is subscribed to receive email notifier
        :param user:
        :return bool:
        """
        obj = MailingList.objects.get_or_create(
            user=user)
        return obj[0].email_notifications

    def is_push_subscribed(user):
        """
        Verify that a user is subscribed to receive push notifier
        :param user:
        :return bool:
        """
        obj = MailingList.objects.get_or_create(
            user=user)
        return obj[0].push_notifications
