"""
    Models for Bookmark app
"""
from django.db import models

# local imports
from authors.apps.articles.models import Articles
from authors.apps.profiles.models import Profile


# Create your models here.
class Bookmark(models.Model):
    """
        Define the model for Bookmark
    """
    # Bookmark can only be either True or False
    BOOKMARK_CHOICES = (
        (True, 'BOOKMARK'),
        (False, 'UNBOOKMARK'),
    )
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Articles, on_delete=models.CASCADE)
    bookmark = models.BooleanField(choices=BOOKMARK_CHOICES, default=True)
    set_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article', 'bookmark')
