from django.shortcuts import get_object_or_404

# Create your views here.
from rest_framework import generics
from .models import Profile
from .serializers import ProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


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
