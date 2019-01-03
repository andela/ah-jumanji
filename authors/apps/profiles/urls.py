"""
    Define the urls where the views for `profiles` are accessible
"""
from django.urls import path
from . import views


urlpatterns = [
    path('profiles/',
         views.ProfilesList.as_view()),
    path('profiles/<str:username>',
         views.GetUserProfile.as_view(),
         name="profile-details"),
    path('profiles/<str:username>/follow',
         views.FollowUser.as_view(),
         name="follow"),
    path('profiles/followers/',
         views.ListAllFollowers.as_view(),
         name="followers"),
    path('profiles/followed/',
         views.ListAllFollowed.as_view(),
         name="followed"),
    path('profiles/users/profiles',
         views.ProfileView.as_view(),
         name='user_profiles'),
]
