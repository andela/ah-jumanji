"""
    Module serializes `UserReaction` model
    :generates JSON from fields in `UserReaction` model
"""

from rest_framework import serializers

# local imports
from authors.apps.user_comment_reaction.models import UserReactionOnComment


class UserReactionOnCommentSerializer(serializers.ModelSerializer):
    """
        Serialize UserReaction model
    """
    class Meta:
        """
            Class Meta
        """
        model = UserReactionOnComment

        fields = ('__all__')
