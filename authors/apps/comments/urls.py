from django.urls import path
from .views import CommentAPIView, CommentUpdateDeleteAPIView

urlpatterns = [
    path('<slug>/comments', CommentAPIView.as_view(), name='comments'),
    path('<slug>/comments/<id>', CommentUpdateDeleteAPIView.as_view(),
         name='specific-comment'),
]
