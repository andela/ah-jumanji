from django.urls import path

from .views import (
    LoginAPIView,
    RegistrationAPIView,
    UserRetrieveUpdateAPIView,
    ResetPasswordRequestAPIView,
    ResetPasswordConfirmAPIView,
    ListUsersAPIView,
    ActivateAPIView
)


urlpatterns = [
    path(
        'user/',
        UserRetrieveUpdateAPIView.as_view(),
        name='user-detail'),
    path(
        'users/', ListUsersAPIView.as_view(),
        name='users-List'),
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
    path(
        'users/activate/<uidb64>/<token>',
        ActivateAPIView.as_view(),
        name='activate'),

]
