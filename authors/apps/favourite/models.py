"""
    Models for Favourite app
"""
from django.db import models

# local imports
from authors.apps.articles.models import Articles
from authors.apps.profiles.models import Profile


# Create your models here.
class Favourite(models.Model):
    """
        Define the model for Favourite
    """
    # Favourite can only be either 1 or -1
    FAVOURITE_CHOICES = (
        (1, 'FAVOURITE'),
        (-1, 'UNFAVOURITE'),
    )
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Articles, on_delete=models.CASCADE)
    favourite = models.IntegerField(choices=FAVOURITE_CHOICES)
    set_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article', 'favourite')
