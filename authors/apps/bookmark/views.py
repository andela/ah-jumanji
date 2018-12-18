"""
    Views for Bookmark app
"""
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# local imports
from authors.apps.bookmark.serializers import BookmarkSerializer
from authors.apps.bookmark.models import Bookmark
from authors.apps.profiles.models import Profile
from authors.apps.user_reactions.views import find_article_helper


# Create your views here.

# Helper functions
def format_response(response):
    """
        Render response into a better format
    """
    user = Profile.objects.get(user=response.user)
    # Formatted bookmark
    bookmark = {
        'id': response.id,
        'article': response.article.slug,
        'bookmark': response.bookmark,
        'set_on': response.set_on,
        'user': {
            'username': user.username,
            'bio': user.bio,
            'profile_photo': user.profile_photo
        }
    }

    return bookmark


class BookmarkView(generics.ListAPIView):
    """
        Define the view for Bookmark
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = BookmarkSerializer

    def set_bookmark(self, article, profile, bookmark):
        """
            Helper method to set the bookmark
        """
        # See if ANY bookmarks by this user on this article exist
        # Remove if found
        try:
            existing_bookmark = Bookmark.objects.get(
                article=article, user=profile)
            existing_bookmark.delete()

        except Bookmark.DoesNotExist:
            # Do nothing if not found
            pass

        data = {
            "article": article.id,
            "user": profile,
            "bookmark": bookmark
        }
        # Save bookmark
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Configure response
        response = {
            "message": "Bookmark successfully made.",
            "bookmark": serializer.data
        }
        status_code = status.HTTP_201_CREATED

        return response, status_code

    def post(self, request):
        """
            POST a bookmark on an article with a given slug
        """
        slug = request.data.get('slug')
        # Find article
        article = find_article_helper(slug)
        user = request.user
        # Use user above to get profile
        profile = Profile.objects.get(user=user)

        bookmark = request.data.get('bookmark')

        # Find out if this user already posted a bookmark on this
        # article, and delete (UNDO) it.
        try:
            # See if user has existing AND same bookmarks the given article
            existing_same_bookmark = Bookmark.objects.get(
                article=article, user=profile, bookmark=bookmark)

            # UNDO a previous bookmark/unbookmark
            existing_same_bookmark.delete()
            response = {
                "message": "You no longer bookmark this article"
            }
            status_code = status.HTTP_200_OK

        # If no SIMILAR bookmark, create one
        except Bookmark.DoesNotExist:
            response, status_code = self.set_bookmark(
                article, profile, bookmark)
        return Response(response, status_code)

    def get(self, request):
        """
            View the all bookmarks on all articles
        """

        # Retrieve all bookmarks
        bookmarks = Bookmark.objects.all()

        # Return bookmarks in a list
        list_bookmarks = []
        # Format bookmark
        for bookmark in bookmarks:

            formatted_bookmarks = format_response(bookmark)
            # Append bookmark to list of bookmarks
            list_bookmarks.append(formatted_bookmarks)

        # Configure response
        response = {
            'bookmarks': list_bookmarks
        }
        return Response(response, status.HTTP_200_OK)


class ArticleBookmarksView(generics.ListAPIView):
    """
        Get bookmarks of a particular article
    """
    def get(self, request, slug):
        """
            GET bookmarks on an article
        """
        # Find article
        article = find_article_helper(slug)

        # Find all bookmarks on this article
        try:
            article_bookmarks = Bookmark.objects.filter(
                article=article)
            formatted_bookmarks = [
                format_response(bookmark) for bookmark in article_bookmarks
            ]

            response = {
                "message": "Bookmarks on article `{}`".format(article.slug),
                "bookmarks": formatted_bookmarks,
                "number_of_bookmarks": {
                    "bookmarks": len(
                        [rxn for rxn in formatted_bookmarks if
                         rxn['bookmark'] is True]),
                    "unbookmarks": len(
                        [rxn for rxn in formatted_bookmarks if
                         rxn['bookmark'] is False]),
                    "total": len(formatted_bookmarks)
                }
            }
            status_code = status.HTTP_200_OK

        # If bookmarks
        except Bookmark.DoesNotExist:
            response = {
                "message": "No bookmarks on article `{}`".format(article.slug)
            }
            status_code = status.HTTP_404_NOT_FOUND

        return Response(response, status_code)
