from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ArticleView.as_view(), name='articles'),
    path('<slug>/', views.ArticleSpecificFunctions.as_view(),
         name='articleSpecific'),
    path('q/', include('authors.apps.search.urls'),
         name="filter-articles")
]
