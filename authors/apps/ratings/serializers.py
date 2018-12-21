from rest_framework import serializers

# local imports
from .models import Rating
from authors.apps.profiles.models import Profile
from authors.apps.articles.models import Articles


class BasicRatingSerializer(serializers.ModelSerializer):
    ''' Write Ratings serializer class '''

    class Meta:
        model = Rating
        fields = ('id', 'rating', 'rater', 'article')


class ArticleDetailsSerializer(serializers.ModelSerializer):
    ''' Excludes non-required article fields '''
    class Meta:
        model = Articles
        exclude = (
            "id",
            "slug",
            "tagList",
            "createdAt",
            "updatedAt",
            'readtime'
        )


class RaterDetailsSerializer(serializers.ModelSerializer):
    ''' Excludes non-required rater fields '''
    class Meta:
        model = Profile
        exclude = (
            "user",
            "first_name",
            "last_name",
            "profile_photo",
            "country",
            "phone_number",
            "twitter_handle",
            "website",
            "created",
            "modified"
        )


class RatingSerializer(serializers.ModelSerializer):
    ''' Read ratings serializer class '''
    article = ArticleDetailsSerializer()
    rater = RaterDetailsSerializer()

    class Meta:
        model = Rating
        fields = ('id', 'rating', 'rater', 'article')
