"""
    Define the views for the `Profile` model
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# local imports
from .models import Profile
from .serializers import ProfileSerializer


# Create your views here.
class ProfileView(APIView):
    """
        Class cntains all the views possible for the `profiles` app
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
            Return the profiles of the logged in User
        """
        # logged in user
        user = request.user
        user_profile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(user_profile)

        # render the response as defined in the API Spec
        formatted_user_profile = {
            "profile": serializer.data
        }

        return Response(formatted_user_profile, status=status.HTTP_200_OK)

    def put(self, request):
        """
            Update items on the `Profile` for logged in user
        """
        # Extract profile data to be updated from request
        profile_data = request.data.get('profile')
        # logged in user
        user = request.user

        # call serializer with extracted data and
        # logged in user (who owns the profile)
        serializer = ProfileSerializer(user, data=profile_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # fetch the updated profile, and return it
        user_profile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(user_profile)

        # render the response as defined in the API Spec
        formatted_user_profile = {
            "profile": serializer.data
        }

        return Response(formatted_user_profile, status=status.HTTP_200_OK)
