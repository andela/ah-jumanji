from django.shortcuts import get_object_or_404
import logging

# Create your views here.
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions, status, reverse

from authors.apps.profiles.models import Profile, Following
from authors.apps.profiles.serializers import (
                                                    ProfileSerializer,
                                                    FollowingSerializer,
                                                    FollowedSerializer,
                                                    FollowersSerializer,
                                                    ProfileSerializer2)

logger = logging.getLogger(__name__)


class ProfilesList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Profile.objects.all()  # Gets all Profiles
    serializer_class = ProfileSerializer


class ProfileDetails(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        profile = get_object_or_404(Profile, username=username)
        data = ProfileSerializer(profile).data
        return Response(data)


class GetUserProfile(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer2

    def get(self, request, *args, **kwargs):
        """fetch the user profile"""

        # verify user and user profile exist
        username = kwargs.get('username', {})
        try:
            user = get_user_model().objects.get(username=username)
            profile = Profile.objects.get(user=user)
        except get_user_model().DoesNotExist:
            raise exceptions.NotFound("user not found")
        except Profile.DoesNotExist:
            raise exceptions.NotFound("The profile has not been created")

        # set the context of the request
        context = {'user': request.user}

        logger.debug(user)
        logger.debug(profile)
        logger.debug(context)
        logger.debug(type(request.user))

        serialized = self.serializer_class(profile, context=context)
        # serialized.is_valid(raise_exception=True)
        return Response(serialized.data)


class FollowUser(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowingSerializer

    def post(self, request, **kwargs):
        """Follow a user"""
        # validate the user exist
        username = kwargs['username']
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            raise exceptions.NotFound("The user specified was not found")

        # check if already following
        profile = Profile.objects.get_or_create(user=request.user)
        profile = profile[0]
        if profile.is_followed(user):
            return Response(
                data={
                    "message": " You are already following %s" % username
                },
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            # add a new follower relationship
            data = {
                "follower": request.user,
                "followed": user,
            }
            relationship = Following.objects.create(**data)

            response = dict(
                message="You are now following %s" % username,
                relationship=self.serializer_class(relationship).data,
                profile=reverse.reverse('profile-details', args=[username])
            )
            return Response(response, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        """unfollow a user"""
        username = kwargs['username']
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            raise exceptions.NotFound("The user specified was not found")

        # check if already following
        profile = Profile.objects.get_or_create(user=request.user)
        profile = profile[0]
        if profile.is_followed(user) is False:
            return Response(
                data={
                    "message": " You are not currently following %s" % username
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # delete the relationship
        data = {
            "follower": request.user,
            "followed": user,
        }
        Following.objects.filter(**data).delete()

        response = dict(
            message="You have successfully unfollowed %s" % username,
            profile=reverse.reverse('profile-details', args=[username])
        )

        return Response(response, status=status.HTTP_200_OK)


class ListAllFollowers(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowersSerializer

    def get(self, request):
        """list all users who follow one"""
        profile = Profile.objects.get_or_create(user=request.user)
        profile = profile[0]
        followers = profile.get_followers()

        if len(followers) == 0:
            return Response(
                {
                    "message": "You currently have no followers"
                               " to display"
                }
            )

        serialized = self.serializer_class(followers, many=True)
        response = dict(
            message="You have %s followers" % followers.count(),
            followers=serialized.data
        )

        return Response(response, status=status.HTTP_200_OK)


class ListAllFollowed(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowedSerializer

    def get(self, request):
        """list all users who follow one"""
        profile = Profile.objects.get_or_create(user=request.user)
        profile = profile[0]
        followed = profile.get_followed()

        if len(followed) == 0:
            return Response(
                {"message": "You are not currently following other users"})

        serialized = self.serializer_class(followed, many=True)

        response = dict(
            message="You are currently following %s users" % followed.count(),
            followed=serialized.data
        )
        return Response(response, status=status.HTTP_200_OK)
