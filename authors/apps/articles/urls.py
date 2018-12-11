from django.urls import path, include
from .views import ArticleView, ArticleSpecificFunctions

urlpatterns = [
    path('articles/', ArticleView.as_view(), name='articles'),
    path('articles/<slug>/', ArticleSpecificFunctions.as_view(),
         name='articleSpecific'),
    path('q/', include('authors.apps.search.urls'),
         name="filter-articles")
]
