from django.urls import path, include
from .views import ArticleView, ArticleSpecificFunctions, ImageUpload

urlpatterns = [
    path('articles/', ArticleView.as_view(),
         name='articles'),
    path('articles/image/upload', ImageUpload.as_view(),
         name='articles_image'),
    path('articles/<slug>/', ArticleSpecificFunctions.as_view(),
         name='articleSpecific'),
    path('q/', include('authors.apps.search.urls'),
         name="filter-articles")
]
