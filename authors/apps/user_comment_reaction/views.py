"""
    Views for user_reaction app
"""
from rest_framework import generics
from rest_framework import exceptions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# local imports
from authors.apps.user_comment_reaction.serializers import (
    UserReactionOnCommentSerializer)
from authors.apps.user_comment_reaction.models import UserReactionOnComment
from authors.apps.profiles.models import Profile
from authors.apps.comments.models import Comment

# Create your views here.


# Helper functions
def find_comment_helper(comment_id):
    """
        Helper method to find comment or raise exception
        :given comment_id
        :return comment or raise 404
    """
    # Find comment
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        # if DoesNotExist exception is raised
        raise exceptions.NotFound(
            "Comment with id `{}` does not exist".format(comment_id))
    return comment


def format_response(reaction):
    """
        Render response into a better format
    """
    user = Profile.objects.get(user=reaction.user)
    # Formatted reaction
    formatted_reaction = {
        'id': reaction.id,
        'comment': reaction.comment.id,
        'reaction': reaction.reaction,
        'set_on': reaction.set_on,
        'user': {
            'username': user.username,
            'bio': user.bio,
            'profile_photo': user.profile_photo
        }
    }

    return formatted_reaction


class UserReactionOnCommentView(generics.ListAPIView):
    """
        Define the view for UserReactionOnComment
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserReactionOnCommentSerializer

    def set_reaction(self, comment, profile, reaction):
        """
            Helper method to set the reaction
        """
        # See if ANY reactions by this user on this comment exist
        # Remove if found
        try:
            existing_reaction = UserReactionOnComment.objects.get(
                comment=comment, user=profile)
            existing_reaction.delete()

        except UserReactionOnComment.DoesNotExist:
            # Do nothing if not found
            pass

        data = {
            "comment": comment.id,
            "user": profile,
            "reaction": reaction
        }
        # Save reaction
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Configure response
        response = {
            "message": "Reaction successfully set.",
            "reaction": serializer.data
        }
        status_code = status.HTTP_201_CREATED

        return response, status_code

    def post(self, request):
        """Post a new comment reaction"""
        comment_id = request.data.get('comment_id')
        # Find comment
        comment = find_comment_helper(comment_id)
        user = request.user
        # Use user above to get profile
        profile = Profile.objects.get(user=user)

        reaction = request.data.get('reaction')

        # Find out if this user already posted a reaction on this
        # comment, and delete (UNDO) it.
        try:
            # See if user has existing AND same reactions on the given comment
            existing_same_reaction = UserReactionOnComment.objects.get(
                comment=comment, user=profile, reaction=reaction)

            # Remove the reaction (UNDO a previous LIKE/DISLIKE)
            existing_same_reaction.delete()
            response = {
                "message": "You nolonger `{}` this comment".format(
                    'LIKE' if reaction in [1, "1"] else 'DISLIKE')
            }
            status_code = status.HTTP_200_OK

        # If no SIMILAR reaction, create one
        except UserReactionOnComment.DoesNotExist:
            response, status_code = self.set_reaction(
                comment, profile, reaction)
        return Response(response, status_code)

    def get(self, request):
        """
            View the reactions on all comments
        """

        # Retrieve all reactions if any
        reactions = UserReactionOnComment.objects.all()

        # Return reactions in a list
        # Format each reaction for better output
        list_reactions = [
            format_response(reaction) for reaction in reactions]
        # Configure response
        response = {
            'reactions': list_reactions
        }
        return Response(response, status.HTTP_200_OK)


class UserReactionOnParticularCommentView(generics.ListAPIView):
    """
        Define a view where the reactions on a particular comment can be
        seen
    """
    def get(self, request, comment_id):
        """Get a specific comment reaction"""
        # Find comment
        comment = find_comment_helper(comment_id)

        # Find all reactions on this comment
        try:
            comment_reactions = UserReactionOnComment.objects.filter(
                comment=comment)
            formatted_reactions = [
                format_response(reaction) for reaction in comment_reactions
            ]

            response = {
                "message": "Reactions on comment with id `{}`".format(
                    comment.id),
                "reactions": formatted_reactions,
                "number_of_reactions": {
                    "likes": len(
                        [rxn for rxn in formatted_reactions if
                         rxn['reaction'] == 1]),
                    "dislikes": len(
                        [rxn for rxn in formatted_reactions if
                         rxn['reaction'] == -1]),
                    "total": len(formatted_reactions)
                }
            }
            status_code = status.HTTP_200_OK

        # If reactions
        except UserReactionOnComment.DoesNotExist:
            response = {
                "message": "No reactions on comment `{}`".format(comment.body)
            }
            status_code = status.HTTP_404_NOT_FOUND

        return Response(response, status_code)
