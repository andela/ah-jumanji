from django.contrib.auth import get_user_model
from notifications.models import Notification
from rest_framework import serializers
from rest_framework.reverse import reverse

from authors.apps.articles.models import Articles
from authors.apps.authentication.serializers import UserSerializer
from authors.apps.notifier.models import MailingList
from authors.apps.profiles.models import Profile, Following
from authors.apps.profiles.serializers import ProfileSerializer, \
    FollowingSerializer


class GenericNotificationField(serializers.RelatedField):
    def to_representation(self, value):
        """serialize notification GenericForeignKey Fields"""
        if isinstance(value, get_user_model()):
            serializer = UserSerializer(value)
        elif isinstance(value, Articles):
            url = reverse('articleSpecific', args=[value.slug, ])
            return url
        elif isinstance(value, Profile):
            serializer = ProfileSerializer(value)
        elif isinstance(value, Following):
            serializer = FollowingSerializer(value)

        return serializer.data


class NotificationSerializer(serializers.ModelSerializer):
    unread = serializers.BooleanField(read_only=True)
    emailed = serializers.BooleanField(read_only=True)

    recipient = GenericNotificationField(read_only=True)
    target = GenericNotificationField(read_only=True)
    actor = GenericNotificationField(read_only=True)
    action_object = GenericNotificationField(read_only=True)
    timesince = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            'id', 'unread', 'emailed', 'actor', 'verb', 'recipient',
            'target', 'action_object', 'timestamp', 'timesince'
        )

    def get_timesince(self, obj):
        """return the time since the notification to now"""
        return obj.timesince()


class MailingListSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = MailingList
        exclude = ('id',)


class CreateMailingListSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = MailingList
        fields = '__all__'
