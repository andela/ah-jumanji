from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='user-detail'),
    path('users/register', RegistrationAPIView.as_view(), name='register'),
    path('users/login', LoginAPIView.as_view(), name='login'),
]
