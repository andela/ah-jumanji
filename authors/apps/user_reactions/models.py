"""
    Models for user_preferences app
"""

from django.db import models

# local imports
from authors.apps.articles.models import Articles
from authors.apps.profiles.models import Profile


# Create your models here.
class UserReaction(models.Model):
    """
        Define the model for user preferences
    """
    # Reaction can only be either 1 or -1
    REACTION_CHOICES = (
        (1, 'LIKE'),
        (-1, 'DISLIKE'),
    )
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, default=0)
    article = models.ForeignKey(
        Articles, on_delete=models.CASCADE, default=0)
    reaction = models.IntegerField(choices=REACTION_CHOICES)
    set_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article', 'reaction')
