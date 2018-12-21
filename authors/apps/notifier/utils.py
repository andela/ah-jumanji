import logging
from smtplib import SMTPException

from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db.models import QuerySet
from notifications.models import Notification
from notifications.signals import notify
from django_q.tasks import Chain

from authors.apps.notifier.models import MailingList

logger = logging.getLogger(__file__)


class Notifier:
    """
    this are custom utility functions for notifier
    """

    @classmethod
    def notify_multiple(cls, actor, recipients, verb, **kwargs):
        """
        Notify multiple recipients about an action
        The recipients must be a queryset in order to make sure it is
        iterable

        :param actor:
        :param recipients:
        :param verb:
        :param kwargs:
        :return:
        """
        # create a chain of async tasks to be run by the task broker
        # sequentiialy
        # create a chain that uses the cache backend
        chain = Chain(cached=True)

        # validate recipients is a valid queryset
        if cls.is_queryset(recipients):
            # iterate through the queryset
            for recipient in recipients:
                if MailingList.is_push_subscribed(recipient):
                    # notify each of the recipients
                    try:
                        # send push notification
                        notify.send(sender=actor, recipient=recipient,
                                    verb=verb, **kwargs)

                        # get the last notification
                        notification = Notification.objects.latest('timestamp')

                        # add the task to the chain
                        chain.append(cls.email_notification, recipient,
                                     notification, **kwargs)

                    except Exception as e:
                        logger.error("%s could notify %s" % (actor, recipient))
                        logger.error(e)
                        raise Exception("Notification failed")

            # run the async chain if there are chained tasks
            if chain.length() > 0:
                chain.run()

    @staticmethod
    def intersect_querysets(qs, *args):
        """
        combine all querysets provided to one queryset with no duplicates
        :param qs: a django Queryset object
        :param args: Queryset objects to be merged
        :return qs:
        """
        # print(args)
        # validate the type of parameter
        if not isinstance(qs, QuerySet):
            logger.error("invalid queryset: %s" % qs)
            raise TypeError("the first parameter passed is not a "
                            "Queryset instance")

        for queryset in args:
            if isinstance(queryset, QuerySet):
                qs = qs.union(queryset)

            else:
                logger.error("invalid queryset: %s" % queryset)
                raise TypeError("parameter %s is not a valid Queryset" %
                                queryset)
        return qs

    @staticmethod
    def is_user(user):
        """
        Validate that a parameter is a valid user instance
        :param arg:
        :return:
        """
        # verify input parameter is valid
        if not isinstance(user, get_user_model()):
            raise TypeError(
                "%s is not a valid %s model" % (user, get_user_model()))
        return True

    @classmethod
    def email_notification(cls, user, notification, **kwargs):
        """Send Email Notifications to users """
        logger.debug("email to be sent to %s " % user)
        subject = kwargs.get('subject', 'jumanji email')
        message = kwargs.get('message', '')

        if cls.is_user(user):
            # verify user is authorised to receive notifications
            if MailingList.is_email_subscribed(user=user):
                try:
                    # compose the email
                    email = EmailMessage(subject, message, to=[user.email])
                    # send the email
                    email.send(fail_silently=False)
                    # mark notification as sent
                    notification.emailed = True
                    notification.save()

                except SMTPException as e:
                    logger.error("error sending email to %s" % user.email)
                    logger.error(e)

    @classmethod
    def get_unread_notifications(cls, user):
        if cls.is_user(user=user):
            # return unread notifications
            return user.notifications.unread()

    @classmethod
    def get_read_notifications(cls, user):
        """
        return all notificationss that a user has read
        :param user:
        :return:
        """
        if cls.is_user(user):
            # return read notifier
            return user.notifications.read()

    def is_queryset(arg):
        """
        check that input is a valid queryset
        :param arg:
        :return bool:
        """
        if not isinstance(arg, QuerySet):
            raise TypeError("%s is not a valid Queryset object" % arg)

        return True
