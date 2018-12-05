"""
    Define the urls where the views for `profiles` are accessible
"""

from django.urls import path

# local imports
from .views import ProfileView


urlpatterns = [
    path('users/profiles', ProfileView.as_view(), name='user_profiles'),
]
