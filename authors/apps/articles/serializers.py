import logging

from django.apps import apps
from rest_framework import serializers

from authors.apps.profiles.serializers import BasicProfileSerializer
from .models import Articles

logger = logging.getLogger(__file__)

TABLE = apps.get_model('articles', 'Articles')


def get_article(slug):
    try:
        article = TABLE.objects.get(slug=slug)
        print(article)
        return article
    except TABLE.DoesNotExist:
        raise serializers.ValidationError(
            "Slug does not contain any matching article.")


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


class ArticleUpdateStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = ['read_count']
