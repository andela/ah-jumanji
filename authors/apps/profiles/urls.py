from django.urls import path
from . import views
from authors.apps.profiles.views import GetUserProfile, \
    FollowUser, ListAllFollowers, ListAllFollowed

urlpatterns = [
    path('profiles/', views.ProfilesList.as_view()),
    path('profiles/<username>', views.ProfileDetails.as_view()),
    path('<str:username>', GetUserProfile.as_view(), name="profile-details"),
    path('<str:username>/follow', FollowUser.as_view(), name="follow"),
    path('followers/', ListAllFollowers.as_view(), name="followers"),
    path('followed/', ListAllFollowed.as_view(), name="followed"),
]
