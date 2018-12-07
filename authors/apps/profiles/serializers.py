import logging

from rest_framework import serializers

from authors.apps.authentication.serializers import UserSerializer
from authors.apps.profiles.models import Profile, Following

logger = logging.getLogger(__name__)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("__all__")


class ProfileSerializer2(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        exclude = ('username', 'email')

    def get_user(self, obj):
        """
        return the username of user
        :param obj:
        :return:
        """

        return obj.user.username

    def get_following(self, obj):
        """
        get current logged in user and verify if they are followers
        :param obj:
        :return:
        """
        requester = self.context['user']
        logger.debug("*" * 100)
        logger.debug(requester)

        # get or create a profile for the current user
        # this will return a queryset of length 1
        profile = Profile.objects.get_or_create(user=requester)
        profile = profile[0]

        return profile.is_followed(obj.user)


class FollowingSerializer(serializers.ModelSerializer):
    follower = UserSerializer()
    followed = UserSerializer()

    class Meta:
        model = Following
        exclude = ('id', 'modified')


class FollowedSerializer(serializers.ModelSerializer):
    followed = UserSerializer()

    class Meta:
        model = Following
        exclude = ('id', 'modified', 'follower')


class FollowersSerializer(serializers.ModelSerializer):
    follower = UserSerializer()

    class Meta:
        model = Following
        exclude = ('id', 'modified', 'followed')
