from django.urls import path

from .views import (
    LoginAPIView,
    RegistrationAPIView,
    UserRetrieveUpdateAPIView,
    ResetPasswordRequestAPIView,
    ResetPasswordConfirmAPIView)

urlpatterns = [
    path(
        'user/',
        UserRetrieveUpdateAPIView.as_view(),
        name='user-detail'),
    path(
        'users/register',
        RegistrationAPIView.as_view(),
        name='register'),
    path(
        'users/login',
        LoginAPIView.as_view(),
        name='login'),
    path(
        'users/reset_password',
        ResetPasswordRequestAPIView.as_view(),
        name="reset_password"),
    path(
        'users/reset_password_confirm/<str:token>',
        ResetPasswordConfirmAPIView.as_view(),
        name="reset_password_confirm"),
]
