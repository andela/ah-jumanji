from django.urls import path
from . import views

urlpatterns = [
    path('profiles/', views.ProfilesList.as_view()),
    path('profiles/<username>', views.ProfileDetails.as_view()),
]
