"""
    Define the urls where the views for `profiles` are accessible
"""
from django.urls import path
from . import views


urlpatterns = [
    path('profiles/', views.ProfilesList.as_view()),
    path('profiles/<str:username>',
         views.ProfileDetails.as_view()),
    path('<str:username>',
         views.GetUserProfile.as_view(),
         name="profile-details"),
    path('<str:username>/follow',
         views.FollowUser.as_view(), name="follow"),
    path('followers/',
         views.ListAllFollowers.as_view(), name="followers"),
    path('followed/',
         views.ListAllFollowed.as_view(), name="followed"),
    path('users/profiles',
         views.ProfileView.as_view(), name='user_profiles'),
]
