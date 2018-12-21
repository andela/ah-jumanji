"""
    Serializes `Favourite` model
"""
from rest_framework import serializers

# local imports
from authors.apps.favourite.models import Favourite


class FavouriteSerializer(serializers.ModelSerializer):
    """
        Favourite  serializer
    """
    class Meta:
        """
            Class Meta
        """
        model = Favourite

        fields = ('__all__')
