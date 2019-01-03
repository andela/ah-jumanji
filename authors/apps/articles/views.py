import logging
import random

from django.utils.text import slugify
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings

from authors.apps.profiles.models import Profile
from .models import Articles
from .serializers import ArticleSerializer, CreateArticleSerializer, \
    ArticleUpdateStatsSerializer

logger = logging.getLogger(__file__)


class ArticleView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleSerializer
    queryset = Articles.objects.all()
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    """
    Posts and gets articles from the model
    """

    def get(self, request, **kwargs):

        context = {
            "request": request,
            "user": request.user
        }
        # Overriding to achieve pagination
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.serializer_class(
                page, context=context, many=True)
            result = self.get_paginated_response(serializer.data)
            return result

    @property
    def paginator(self):
        # paginator instance associated with this view
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):

        # counters return of a single page of articles or None if disabled
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(
            queryset,
            self.request,
            view=self)

    def get_paginated_response(self, data):

        # return paginated style for given output data
        try:
            return self.paginator.get_paginated_response(data)

        except AssertionError:
            assert self.paginator is not None
            return Response({'message': 'cannot return paginated data'})

    def post(self, request, **kwargs):
        """Create a new article"""
        passed_data = request.data
        posted_data = {
            "slug": self.slugify_string(passed_data['title']),
            "title": passed_data['title'],
            "description": passed_data['description'],
            "body": passed_data['body'],
            "tagList": passed_data['tagList'],
            "readtime": self.readTime(passed_data['body']),
            "author": Profile.objects.get(username=request.user.username)
        }

        context = {
            "request": request,
            "user": request.user
        }
        serializer = CreateArticleSerializer(data=posted_data)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
            article = Articles.objects.get(slug=posted_data.get('slug', {}))

            serialized = self.serializer_class(article, context=context)
            return Response({"message": "posted", 'article': serialized.data},
                            status.HTTP_201_CREATED)

        except Exception as what_is_this:
            return Response({"error": "{}".format(what_is_this)},
                            status.HTTP_400_BAD_REQUEST)

    def slugify_string(self, string):
        processed_slug = slugify(string)
        slug_int = random.randint(100, 1000000)
        new_slug = '{}-{}'.format(processed_slug, slug_int)
        return new_slug

    def readTime(self, story):
        story_list = story.split(" ")
        resolved_time = (len(story_list)) / 200
        read_time = round(resolved_time)
        return read_time


class ArticleSpecificFunctions(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleSerializer

    def read_article(self, request, article):
        user = request.user
        if user != article.author.username:
            read_count = article.read_count
            read_count += 1
            new_article = {
                'read_count': read_count
            }
            serializer = ArticleUpdateStatsSerializer(data=new_article)
            serializer.is_valid(raise_exception=True)
            serializer.update(article, new_article)

    def get(self, request, slug):
        """Retrieve a specific article"""
        context = {
            "request": request,
            "user": request.user
        }

        try:
            article = Articles.objects.get(slug=slug)
            self.read_article(request, article)

            serialized = self.serializer_class(article, context=context)
            return Response({"articles": serialized.data},
                            status.HTTP_200_OK)

        except Exception as error:
            print('Received error is : {}'.format(error))
            return Response({"message": "Article does not exist"},
                            status.HTTP_404_NOT_FOUND)

    def put(self, request, slug):
        """Edit a specific article"""
        context = {
            "request": request,
            "user": request.user
        }

        payload = request.data  # values to update

        try:
            article = Articles.objects.get(slug=slug)
            serializer = CreateArticleSerializer(
                article, data=payload, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()

            serialized = self.serializer_class(article, context=context)
            return Response({"message": "Update successful",
                             "article": serialized.data},
                            status.HTTP_200_OK)

        except Exception as what:
            return Response({'error': "{}".format(what)})

    def delete(self, request, slug, **kwargs):
        """Delete a specific article"""
        try:
            Articles.objects.get(slug=slug).delete()

            return Response({"message":
                             "Article {} deleted successfully".format(slug)},
                            status.HTTP_200_OK)

        except Exception:
            return Response({"message": "Could not find that article"},
                            status.HTTP_400_BAD_REQUEST)
