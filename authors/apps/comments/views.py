from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import CommentSerializer
from authors.apps.articles.models import Articles
from authors.apps.profiles.models import Profile
from rest_framework import exceptions

# local imports
from .models import Comment

# Create your views here.


class CommentAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def post(self, request, slug):

        try:
            article = Articles.objects.get(slug=slug)
        except Articles.DoesNotExist:
            raise exceptions.NotFound("Article Not found")

        payload = request.data.get("comment", {})
        comment = payload['body']

        data = {
            "body": comment,
            "commenter": request.user,
            "article": article.id
        }
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        response = {
            "message": "Comment created successfully",
            "comment": serializer.data
        }

        return Response(response, status=status.HTTP_201_CREATED)

    def get(self, request, slug):

        try:
            comments = Comment.objects.all()
        except Comment.DoesNotExist:
            raise exceptions.NotFound("No comments found")

        all_comments = []
        for comment in comments:
            author = Profile.objects.get(user_id=comment.commenter_id)
            comment = {
                "id": comment.id,
                "createdAt": comment.createdAt,
                "updatedAt": comment.updatedAt,
                "body": comment.body,
                "author": {
                    "username": author.username,
                    "bio": author.bio,
                    "image": author.profile_photo
                }
            }
            all_comments.append(comment)
        response = {
            "comment": all_comments
        }
        return Response(response, status=status.HTTP_200_OK)


class CommentUpdateDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def put(self, request, slug, id):
        try:
            updated_comment = Comment.objects.get(id=id)

        except Comment.DoesNotExist:
            raise exceptions.NotFound("Comment does not exist")

        data = request.data.get("comment", {})

        serializer = self.serializer_class(
            updated_comment, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = {
            "message": "Comment updated successfully",
            "comment": serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)

    def delete(self, request, slug, id):
        try:
            deleted_comment = Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            raise exceptions.NotFound("Comment does not exist")

        deleted_comment.delete()
        response = {
            "message": "Comment deleted successfully!"
        }
        return Response(response, status=status.HTTP_200_OK)
