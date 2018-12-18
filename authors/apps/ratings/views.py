from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions


# local imports
from .serializers import RatingSerializer, BasicRatingSerializer
from .models import Rating
from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User


# Create your views here.
class RatingAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RatingSerializer

    def post(self, request, slug):
        ''' Post a rating '''

        # Fetch article
        try:
            article = Articles.objects.get(slug=slug)
        except Articles.DoesNotExist:
            raise exceptions.NotFound("Article Not found")

        # Get article author
        article_author = User.objects.get(id=article.author_id)
        if article_author.email == request.user.email:
            response = ({"message": "You cannot rate your own article"})
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        payload = request.data
        rating_data = {
            "rating": payload['rating'],
            "rater": request.user,
            "article": article.id
        }

        # check if rating exists for the article
        try:
            current_rating = Rating.objects.get(rater_id=request.user.id)
            # perform an update if exists
            serializer = BasicRatingSerializer(
                current_rating, data=request.data, partial=True)

        except Rating.DoesNotExist:
            # create a new rating if does not exists
            serializer = BasicRatingSerializer(data=rating_data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        rating = Rating.objects.get(rater_id=request.user.id)
        serialized = self.serializer_class(rating)

        response = ({"message": "Rating added successfully",
                     "rating": serialized.data
                     })

        return Response(response, status=status.HTTP_201_CREATED)

    def get(self, request, slug):
        ''' Get weighed average rating of an article '''
        # Fetch the article
        try:
            article = Articles.objects.get(slug=slug)
        except Articles.DoesNotExist:
            raise exceptions.NotFound("Article Not found")

        average_rating = Rating.get_average_rating(article.id)
        response = {
            "slug": article.slug,
            "title": article.title,
            "body": article.body,
            "rating": average_rating
        }

        return Response(response, status=status.HTTP_200_OK)


class DeleteRatingAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RatingSerializer

    def delete(self, request, slug, id):

        # Check if the specific ratings exists
        try:
            delete_rating = Rating.objects.get(id=id)
        except Rating.DoesNotExist:
            raise exceptions.NotFound("Rating Not found")

        if delete_rating.rater_id != request.user.id:
            return Response(
                {"message": "Cannot perform this action!"},
                status=status.HTTP_403_FORBIDDEN)

        delete_rating.delete()
        return Response({"message": "Rating removed successfully"},
                        status=status.HTTP_200_OK)
