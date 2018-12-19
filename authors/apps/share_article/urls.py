from django.urls import path
from .views import ShareArticleView


urlpatterns = [
    path('articles/<str:slug>/share/<str:provider>',
         ShareArticleView.as_view(),
         name='share_article'),
]
