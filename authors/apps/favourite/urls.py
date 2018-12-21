"""
    Define the urls where the views for `favourite` are accessible
"""
from django.urls import path

# local imports
from authors.apps.favourite.views import (
    FavouriteView, ArticleFavouritesView
)


urlpatterns = [
    path(
        'all/', FavouriteView.as_view(),
        name='favourites'),
    path(
        'single/<str:slug>', ArticleFavouritesView.as_view(),
        name='article_favourites'),
]
