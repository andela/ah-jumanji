"""
    Views for Favourite app
"""
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# local imports
from authors.apps.favourite.serializers import FavouriteSerializer
from authors.apps.favourite.models import Favourite
from authors.apps.profiles.models import Profile
from authors.apps.user_reactions.views import find_article_helper


# Create your views here.

# Helper functions
def format_response(response):
    print(response)
    """
        Render response into a better format
    """
    user = Profile.objects.get(user=response.user)
    # Formatted favourite
    favourite = {
        'id': response.id,
        'article': response.article.slug,
        'favourite': response.favourite,
        'set_on': response.set_on,
        'user': {
            'username': user.username,
            'bio': user.bio,
            'profile_photo': user.profile_photo
        }
    }

    return favourite


class FavouriteView(generics.ListAPIView):
    """
        Define the view for Favourite
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = FavouriteSerializer

    def set_favourite(self, article, profile, favourite):
        """
            Helper method to set the favourite
        """
        # See if ANY favourites by this user on this article exist
        # Remove if found
        try:
            existing_favourite = Favourite.objects.get(
                article=article, user=profile)
            existing_favourite.delete()

        except Favourite.DoesNotExist:
            # Do nothing if not found
            pass

        data = {
            "article": article.id,
            "user": profile,
            "favourite": favourite
        }
        # Save favourite
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Configure response
        response = {
            "message": "Favourite successfully made.",
            "favourite": serializer.data
        }
        status_code = status.HTTP_201_CREATED

        return response, status_code

    def post(self, request):
        """
            POST a favourite on an article with a given slug
        """
        slug = request.data.get('slug')
        # Use user above to get profile
        profile = Profile.objects.get(user=request.user)

        favourite = request.data.get('favourite')

        # Find out if this user already posted a favourite on this
        # article, and delete (UNDO) it.
        try:
            # See if user has existing AND same favourites the given article
            existing_same_favourite = Favourite.objects.get(
                article=find_article_helper(slug),
                user=profile,
                favourite=favourite
                )

            # UNDO a previous favourite/unfavourite
            existing_same_favourite.delete()
            response = {
                "message": "You no longer `{}` this article".format(
                    'FAVOURITE' if favourite in [1, "1"] else 'UNFAVOURITE')
            }
            status_code = status.HTTP_200_OK

        # If no SIMILAR favourite, create one
        except Favourite.DoesNotExist:
            response, status_code = self.set_favourite(
                find_article_helper(slug), profile, favourite)
        return Response(response, status_code)

    def get(self, request):
        """
            View the all favourites on all articles
        """
        # Retrieve all favourites if any
        favourites = Favourite.objects.all()

        # Return favourites in a list
        list_favourites = []
        # Format favourite
        for favourite in favourites:
            print('fav:')
            print(favourite)

            formatted_favourites = format_response(favourite)
            # Append favourite to list of favourites
            list_favourites.append(formatted_favourites)

        # Configure response
        response = {
            'favourites': list_favourites
        }
        return Response(response, status.HTTP_200_OK)


class ArticleFavouritesView(generics.ListAPIView):
    """
        Get favourites of a particular article
    """
    def get(self, request, slug):
        """
            GET favourites on an article
        """
        # Find article
        article = find_article_helper(slug)

        # Find all favourites on this article
        try:
            article_favourites = Favourite.objects.filter(
                article=article)
            formatted_favourites = [
                format_response(favourite) for favourite in article_favourites
            ]

            response = {
                "message": "Favourites on article `{}`".format(article.slug),
                "favourites": formatted_favourites,
                "number_of_favourites": {
                    "favourites": len(
                        [rxn for rxn in formatted_favourites if
                         rxn['favourite'] == 1]),
                    "unfavourites": len(
                        [rxn for rxn in formatted_favourites if
                         rxn['favourite'] == -1]),
                    "total": len(formatted_favourites)
                }
            }
            status_code = status.HTTP_200_OK

        # If favourites
        except Favourite.DoesNotExist:
            response = {
                "message": "No favourites on article `{}`".format(article.slug)
            }
            status_code = status.HTTP_404_NOT_FOUND

        return Response(response, status_code)
