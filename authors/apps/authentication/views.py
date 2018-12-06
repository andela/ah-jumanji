from rest_framework import status
from rest_framework import generics
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from .models import User
from .backends import JWTAuthentication
import jwt
from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
)

# Instantiate base classes
instance = User()
auth = JWTAuthentication()


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # generate and return an authorised token

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})
        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ListUsersAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
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


class ResetPasswordRequestAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
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


class ResetPasswordConfirmAPIView(RetrieveUpdateAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def put(self, request, token):
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
