from rest_framework import serializers
import logging

from .models import Articles
from authors.apps.profiles.serializers import BasicProfileSerializer

logger = logging.getLogger(__file__)


class ArticleSerializer(serializers.ModelSerializer):

    author = serializers.SerializerMethodField()

    class Meta:
        model = Articles
        fields = "__all__"

    def get_author(self, obj):
        author_profile = obj.author
        serialized = BasicProfileSerializer(
            author_profile, context=self.context)

        return serialized.data


class CreateArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Articles
        fields = "__all__"


class BasicArticleSerializer(serializers.ModelSerializer):
    """A basic article information serializer"""
    author = serializers.SerializerMethodField()

    class Meta:
        model = Articles
        exclude = ('id',)

    def get_author(self, obj):
        return obj.author.username
