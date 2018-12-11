from django.urls import path
from .views import CommentAPIView, CommentUpdateDeleteAPIView

urlpatterns = [
    path(
        'articles/<slug>/comments',
        CommentAPIView.as_view(),
        name='comments'),
    path(
        'articles/<slug>/comments/<id>',
        CommentUpdateDeleteAPIView.as_view(),
        name='specific-comment'),
]
