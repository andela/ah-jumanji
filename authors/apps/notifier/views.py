# Create your views here.
import logging

from notifications.models import Notification
from rest_framework import generics, exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authors.apps.notifier.models import MailingList
from authors.apps.notifier.serializers import MailingListSerializer, \
    CreateMailingListSerializer, NotificationSerializer
from authors.apps.notifier.utils import Notifier

logger = logging.getLogger(__name__)


class GetMailingList(generics.ListAPIView):
    """View the entire current mailing list"""
    queryset = MailingList.objects.all()
    serializer_class = MailingListSerializer
    permission_classes = (IsAuthenticated,)


class ViewUpdateMailingList(generics.GenericAPIView):
    """Retrieve and update the mailing status"""
    serializer_class = CreateMailingListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """retrieve the mailing list status of the current user"""
        user = request.user
        status = MailingList.objects.get_or_create(user=user)
        status = status[0]
        serialized = MailingListSerializer(status)

        return Response(serialized.data)

    def put(self, request):
        """Modify the mailing status"""
        # collect input and current context
        data = request.data
        status = MailingList.objects.get_or_create(user=request.user)
        status = status[0]

        # validate and save the input
        serialized = self.serializer_class(instance=status, data=data,
                                           context=request, partial=True)
        serialized.is_valid(raise_exception=True)
        serialized.save()

        # return a more detailed response
        status = MailingList.objects.get(user=request.user)
        serialized = MailingListSerializer(status)
        return Response(serialized.data)


class GetNotifications(generics.GenericAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        """Get all unread notifications"""
        user = request.user
        notifications = Notifier.get_unread_notifications(user=user)

        logger.error(notifications)

        if notifications.count() == 0:
            # return a custom message if there are no notifications
            res = dict(
                message="You have no notifications to display"
            )
            return Response(res)
        else:
            # return notifications and  metadata
            serialized = self.serializer_class(notifications,
                                               context=request, many=True)
            res = dict(
                count=len(notifications),
                notifications=serialized.data
            )

            return Response(res)


class GetReadNotifications(generics.GenericAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        """Get all  notifications that are marked as read"""
        user = request.user
        notifications = Notifier.get_read_notifications(user=user)

        logger.error(notifications)

        if notifications.count() == 0:
            # return a custom message if there are no notifications
            res = dict(
                message="You have no notifications to display"
            )
            return Response(res)
        else:
            # return notifications and  metadata
            serialized = self.serializer_class(notifications,
                                               context=request, many=True)
            res = dict(
                count=len(notifications),
                notifications=serialized.data
            )

            return Response(res)


class ReadNotifications(generics.GenericAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request, id):
        """read a notification and mark as read"""
        notification_id = id

        if notification_id:
            try:
                notification = Notification.objects.get(pk=notification_id)
            except Notification.DoesNotExist:
                raise exceptions.NotFound(
                    "The notification %s was not found" % notification_id)

            # mark a notification as read
            notification.mark_as_read()

            # serialize notification
            serialized = self.serializer_class(notification)

            return Response(serialized.data)


class UnreadNotification(generics.GenericAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request, id):
        """mark notification as unread"""
        notification_id = id

        if notification_id:
            try:
                notification = Notification.objects.get(pk=notification_id)
            except Notification.DoesNotExist:
                raise exceptions.NotFound(
                    "The notification %s was not found" % notification_id)

            # mark a notification as unread
            notification.mark_as_unread()

            # serialize notification
            serialized = self.serializer_class(notification)

            return Response(serialized.data)


class MarkNotificationsAsRead(generics.GenericAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        """Mark all notifications as read"""
        user = request.user
        notifications = Notifier.get_unread_notifications(user=user)

        notifications.mark_all_as_read()

        res = dict(
            message="Notifications marked as read"
        )

        return Response(res)
