from django.urls import path

# local imports
from .views import RatingAPIView, DeleteRatingAPIView

urlpatterns = [
    path(
        'articles/<slug>/rating',
        RatingAPIView.as_view(),
        name='ratings'
    ),
    path(
        'articles/<slug>/rating/<id>',
        DeleteRatingAPIView.as_view(),
        name='delete_rating'
    ),
]
