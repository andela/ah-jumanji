"""
    Module serializes `Profile` model
    :generates JSON from fields in `Profile` model
"""

from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
        Generate JSON from `Profile model
    """

    class Meta:
        """
            Map fields in `Profile` model with serializer's JSON params
        """
        model = Profile

        # Collect all the fields in `Profile` model
        fields = '__all__'

        # read only fiels - not editable
        read_only_fields = [
            'user',
        ]

    def update(self, instance, prof_data):
        """
            Update profile items
        """
        # For every item provided in the payload,
        # amend the profile accordingly
        for(key, value) in prof_data.items():
            setattr(instance.profile, key, value)
        instance.save()

        return instance
