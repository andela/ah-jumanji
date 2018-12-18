"""
    Define route where UserReactionView is accessible on API
"""

from django.urls import path

# local imports
from authors.apps.user_comment_reaction.views import (
    UserReactionOnCommentView, UserReactionOnParticularCommentView
)


urlpatterns = [
    path(
        'comments/reactions',
        UserReactionOnCommentView.as_view(),
        name='comment_reactions'),
    path(
        'comments/reactions/<comment_id>',
        UserReactionOnParticularCommentView.as_view(),
        name='reactions_per_comment'),
]
