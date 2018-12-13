from rest_framework import serializers
from .models import Comment
from authors.apps.profiles.models import Profile


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = "__all__"

    def get_author(self, obj):
        profile = Profile.objects.get(user=obj.commenter)
        return CommentAuthorDetailsSerializer(profile).data


class CommentAuthorDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        exclude = (
            'user',
            'first_name',
            'last_name',
            'country',
            'phone_number',
            'twitter_handle',
            'website',
            'created',
            'modified')
