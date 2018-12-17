"""
    Define route where UserReactionView is accessible on API
"""

from django.urls import path

# local imports
from authors.apps.user_reactions.views import (
    UserReactionView, UserReactionOnParticularArticleView
)


urlpatterns = [
    path(
        'articles/reactions',
        UserReactionView.as_view(),
        name='reactions'),
    path(
        'articles/reactions/<slug>',
        UserReactionOnParticularArticleView.as_view(),
        name='reactions_per_article'),
]
