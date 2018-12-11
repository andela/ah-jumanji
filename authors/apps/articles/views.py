from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings

from .models import Articles
from .serializers import ArticleSerializer


class ArticleView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleSerializer
    queryset = Articles.objects.all()
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    """
    Posts and gets articles from the model
    """

    def get(self, request, **kwargs):

        # Overriding to achieve pagination
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
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


    @staticmethod
    def post(request, **kwargs):
        """Create a new article"""
        passed_data = request.data
        serializer = ArticleSerializer()
        result = serializer.posting_articles(passed_data)
        if result == 'Could not post':
            return Response({"message": result}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "posted", 'article': result},
                            status.HTTP_201_CREATED)


class ArticleSpecificFunctions(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleSerializer

    @staticmethod
    def get(request, slug):
        """Retrieve a specific article"""
        try:
            serializer = ArticleSerializer()
            result = serializer.get_specific_objects(slug)
            return Response({"articles": result}, status.HTTP_200_OK)

        except Exception as error:
            print('Received error is : {}'.format(error))
            return Response({"message": "Article does not exist"},
                            status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def put(request, slug):
        """Edit a specific article"""
        payload = request.data  # values to update
        serializer = ArticleSerializer()
        result = serializer.updateArticle(payload, slug)
        if result == 'error':
            return ({'error': 'Could not update'},
                    status.HTTP_304_NOT_MODIFIED)

        return Response({"message": result,
                         "articles": serializer.get_all_objects()},
                        status.HTTP_200_OK)

    @staticmethod
    def delete(request, slug, **kwargs):
        """Delete a specific article"""
        serializer = ArticleSerializer()
        result = serializer.deleteArticle(slug)
        if result == 'Article does not exist':
            return Response({"message": result}, status.HTTP_400_BAD_REQUEST)

        return Response({"message": result}, status.HTTP_200_OK)
