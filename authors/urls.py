"""authors URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Jumanji Authors Haven API')

urlpatterns = [
    path('', schema_view),
    path(
        'admin/',
        admin.site.urls),
    path(
        'api/',
        include('authors.apps.authentication.urls')),
    path(
        'api/',
        include('authors.apps.profiles.urls')),
    path(
        'api/',
        include('authors.apps.articles.urls')),
    path(
        'api/',
        include('authors.apps.comments.urls')),
    path(
        'api/',
        include('authors.apps.profiles.urls')),
    path(
        'api/',
        include('authors.apps.user_reactions.urls')),
    path(
        'api/',
        include('authors.apps.user_comment_reaction.urls')),
    path(
        'api/articles/favourites/',
        include('authors.apps.favourite.urls')),
    path(
        'api/articles/bookmarks/',
        include('authors.apps.bookmark.urls')),
    path(
        'api/',
        include('authors.apps.ratings.urls')),
    path(
        'api/',
        include('authors.apps.notifier.urls')),
    path(
        'api/',
        include('authors.apps.share_article.urls')),
    path(
        'api/',
        include('authors.apps.read_stats.urls')),
]
