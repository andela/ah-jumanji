from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import ArticleSerializer


class ArticleView(views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleSerializer
    """Posts and gets articles from the model"""

    def get(self, request):
        """The get request function"""
        serializer = self.serializer_class
        result = serializer.get_all_objects()
        length = len(result)
        return Response(
            {"articles": result, "articlesCount": length}, status.HTTP_200_OK)

    @staticmethod
    def post(request, **kwargs):
        passed_data = request.data
        serializer = ArticleSerializer()
        result = serializer.posting_articles(passed_data)
        if result == 'Could not post':
            return Response({"message": result}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "posted", 'article': result},
                            status.HTTP_201_CREATED)


class ArticleSpecificFunctions(views.APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request, slug):
        """The get specific request function"""
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
        serializer = ArticleSerializer()
        result = serializer.deleteArticle(slug)
        if result == 'Article does not exist':
            return Response({"message": result}, status.HTTP_400_BAD_REQUEST)

        return Response({"message": result}, status.HTTP_200_OK)
