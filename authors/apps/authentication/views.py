import jwt
import random
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.generics import CreateAPIView, \
    GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .backends import JWTAuthentication
from .backends import account_activation_token
from .confirmation import send_confirmation_email
from .models import User
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    SocialAuthenticator
)
from social_django.utils import load_strategy, load_backend
from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social_core.exceptions import MissingBackend
from social.exceptions import AuthAlreadyAssociated


# Instantiate base classes
instance = User()
auth = JWTAuthentication()
User = get_user_model()


class RegistrationAPIView(GenericAPIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request, **kwargs):
        """Register a new user"""
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        send_confirmation_email(user, request)

        # generate and return an authorised token
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request, **kwargs):
        """Login a user"""
        user = request.data.get('user', {})
        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ListUsersAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveUpdateAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetPasswordRequestAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def post(self, request, **kwargs):
        """User reset password"""
        email = request.data.get('email', None)
        protocol = 'https://' if request.is_secure() else 'http://'
        current_site = get_current_site(request)
        user = instance.get_user(email=email)

        # checks if email is provided
        if not email:
            message = {"message": "Please provide an email address"}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        # Checks if user is registered
        if not user:
            message = {"message": "Could not find that email address!"}
            return Response(message, status=status.HTTP_404_NOT_FOUND)

        # Send reset mail to registered user
        token = auth.generate_reset_token(email)
        reset_url = protocol + current_site.domain + \
            reverse('reset_password_confirm',
                    kwargs={"token": token})
        subject, from_email, to = (
            'Authors Haven Reset Password', settings.EMAIL_HOST_USER, email)
        text_content = 'Reset Password'
        html_content = "<p>Click on this <a href='" + \
            reset_url + "'>Link<a> to reset your password</p>"
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return Response(
            {
                "message":
                "A password reset email has been sent to your account!"},
            status=status.HTTP_200_OK)


class ResetPasswordConfirmAPIView(GenericAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def put(self, request, token):
        """Change user password"""
        payload = jwt.decode(token, settings.SECRET_KEY)
        user = instance.get_user(email=payload["email"])

        password = request.data.get('password', None)
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user.set_password(password)
        user.save()

        return Response(
            {"message": "Your password has been updated successfully!"},
            status=status.HTTP_200_OK)


class RefreshToken(CreateAPIView):
    """
    A view to refresh existing JWT tokens
    """
    pass


class ActivateAPIView(GenericAPIView):
    """
    This view updates the user to activated if tokens are only valid
    """
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token, **kwargs):
        """Activate user account"""
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user.is_active is True:
            return Response({'message': 'Activation link has expired'})

        if user is not None and account_activation_token.check_token(
                user, token):
            # activate user and login:
            user.is_active = True
            user.save()

            return Response({'message': 'Activation was successful'})

        else:
            return Response({'message': 'Activation link is invalid'})


class SocialAuthenticate(GenericAPIView):
    """processes logins form social platforms"""
    permission_classes = (AllowAny,)
    serializer_class = SocialAuthenticator
    login_serializer = LoginSerializer

    def post(self, request, **kwargs):
        """Receives payload data and retrieves user datails"""
        payload = request.data
        serializer = self.serializer_class(data=payload)
        serializer.is_valid(raise_exception=True)
        provider = serializer.data.get("provider")

        try:
            strategy = load_strategy(request)
            backend = load_backend(
                strategy=strategy, name=provider, redirect_uri=None)
            baseOAuth1 = isinstance(backend, BaseOAuth1)
            baseOAuth2 = isinstance(backend, BaseOAuth2)
            if baseOAuth1:
                # Check if access token is passed
                if "access_token_secret" in request.data:
                    token = {
                        'oauth_token': payload.get('access_token'),
                        'oauth_token_secret': payload.get(
                            'access_token_secret'),
                    }
                else:
                    return Response(
                        {"error": "Access token secret is required"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            elif baseOAuth2:
                token = payload.get('access_token')

            else:
                return Response({'message':
                                 'Could not identify Oauth property used'})

        except MissingBackend:
            return Response({"error": "The Provider is invalid"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            response_user = backend.do_auth(token, ajax=True)

        except AuthAlreadyAssociated:
            # You can't associate a social account with more than user
            return Response({"message": "Tha account is in use"},
                            status=status.HTTP_400_BAD_REQUEST)

        except BaseException as what:
            return Response({"message": "access_token/token_secret error",
                             "error": str(what)},
                            status=status.HTTP_400_BAD_REQUEST)

        # login(request, user)
        response_data = {
            'username': response_user.username,
            'email': '{}'.format(response_user),
            'provider': provider
        }

        user = User.objects.get(username=response_data["username"])
        user.is_active = True

        # If twitter
        if provider == 'twitter':
            user.email = "{}.{}@twit.auth".format(response_user.username,
                                                  random.randint(1, 1000))
        user.save()

        token = auth.generate_social_token(response_user.username)

        result = {
            'login_data': response_data,
            'social_token': 'Token {}'.format(token)
        }
        return Response(result, status=status.HTTP_200_OK)
