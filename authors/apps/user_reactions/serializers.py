"""
    Module serializes `UserReaction` model
    :generates JSON from fields in `UserReaction` model
"""

from rest_framework import serializers

# local imports
from authors.apps.user_reactions.models import UserReaction


class UserReactionSerializer(serializers.ModelSerializer):
    """
        Serialize UserReaction model
    """
    class Meta:
        """
            Class Meta
        """
        model = UserReaction

        fields = ('__all__')
