"""
    Serializes `Bookmark` model
"""
from rest_framework import serializers

# local imports
from authors.apps.bookmark.models import Bookmark


class BookmarkSerializer(serializers.ModelSerializer):
    """
        Bookmark  serializer
    """
    class Meta:
        """
            Class Meta
        """
        model = Bookmark

        fields = ('__all__')
