"""
    Views for user_reaction app
"""
from rest_framework import generics
from rest_framework import exceptions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# local imports
from authors.apps.user_reactions.serializers import UserReactionSerializer
from authors.apps.user_reactions.models import UserReaction
from authors.apps.profiles.models import Profile
from authors.apps.articles.models import Articles


# Create your views here.

# Helper functions
def find_article_helper(slug):
    """
        Helper method to find article or raise exception
        :given slug
        :return article or raise 404
    """
    # Find article
    try:
        article = Articles.objects.get(slug=slug)
    except Articles.DoesNotExist:
        # if DoesNotExist exception is raised
        raise exceptions.NotFound(
            "Article with slug `{}` does not exist".format(slug))
    return article


def format_response(reaction):
    """
        Render response into a better format
    """
    user = Profile.objects.get(user=reaction.user)
    # Formatted reaction
    reaction = {
        'id': reaction.id,
        'article': reaction.article.slug,
        'reaction': reaction.reaction,
        'set_on': reaction.set_on,
        'user': {
            'username': user.username,
            'bio': user.bio,
            'profile_photo': user.profile_photo
        }
    }

    return reaction


class UserReactionView(generics.ListAPIView):
    """
        Define the view for UserReaction
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserReactionSerializer

    def set_reaction(self, article, profile, reaction):
        """
            Helper method to set the reaction
        """
        # See if ANY reactions by this user on this article exist
        # Remove if found
        try:
            existing_reaction = UserReaction.objects.get(
                article=article, user=profile)
            existing_reaction.delete()

        except UserReaction.DoesNotExist:
            # Do nothing if not found
            pass

        data = {
            "article": article.id,
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
        """
            POST a reaction on an article with a given slug
        """
        slug = request.data.get('slug')
        # Find article
        article = find_article_helper(slug)
        user = request.user
        # Use user above to get profile
        profile = Profile.objects.get(user=user)

        reaction = request.data.get('reaction')

        # Find out if this user already posted a reaction on this
        # article, and delete (UNDO) it.
        try:
            # See if user has existing AND same reactions the given article
            existing_same_reaction = UserReaction.objects.get(
                article=article, user=profile, reaction=reaction)

            # Remove the reaction (UNDO a previous LIKE/DISLIKE)
            existing_same_reaction.delete()
            response = {
                "message": "You nolonger `{}` this article".format(
                    'LIKE' if reaction in [1, "1"] else 'DISLIKE')
            }
            status_code = status.HTTP_200_OK

        # If no SIMILAR reaction, create one
        except UserReaction.DoesNotExist:
            response, status_code = self.set_reaction(
                article, profile, reaction)
        return Response(response, status_code)

    def get(self, request):
        """
            View the all reactions on all articles
            GET /api/articles/reactions/
        """

        # Retrieve all reactions if any
        reactions = UserReaction.objects.all()

        # Return reactions in a list
        list_reactions = []
        # Format reaction
        for reaction in reactions:
            formatted_reaction = format_response(reaction)

            # Append reaction to list of reactions
            list_reactions.append(formatted_reaction)
        # Configure response
        response = {
            'reactions': list_reactions
        }
        return Response(response, status.HTTP_200_OK)


class UserReactionOnParticularArticleView(generics.ListAPIView):
    """
        Define a view where the reactions on a particular article can be
        seen
    """
    def get(self, request, slug):
        """
            GET /api/articles/reactions/<slug>
        """
        # Find article
        article = find_article_helper(slug)

        # Find all reactions on this article
        try:
            article_reactions = UserReaction.objects.filter(
                article=article)
            formatted_reactions = [
                format_response(reaction) for reaction in article_reactions
            ]

            response = {
                "message": "Reactions on article `{}`".format(article.slug),
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
        except UserReaction.DoesNotExist:
            response = {
                "message": "No reactions on article `{}`".format(article.slug)
            }
            status_code = status.HTTP_404_NOT_FOUND

        return Response(response, status_code)
