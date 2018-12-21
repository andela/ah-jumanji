"""
    Define the urls where the views for `bookmarks` are accessible
"""
from django.urls import path

# local imports
from authors.apps.bookmark.views import (
    BookmarkView, ArticleBookmarksView
)


urlpatterns = [
    path(
        'all/', BookmarkView.as_view(),
        name='bookmarks'),
    path(
        'single/<str:slug>', ArticleBookmarksView.as_view(),
        name='article_bookmarks'),
]
