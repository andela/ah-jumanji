from django.db import models
from authors.apps.profiles.models import Profile
from authors.apps.articles.models import Articles


class Readers(models.Model):
    reader = models.ForeignKey(Profile,
                               related_name='read_by',
                               on_delete=models.CASCADE,
                               null=False, blank=False,)
    article = models.ForeignKey(Articles,
                                on_delete=models.CASCADE,
                                null=False, blank=False,)
    last_read = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'read_stats'

    def __str__(self):
        """Print out as title."""
        return self.article.title
