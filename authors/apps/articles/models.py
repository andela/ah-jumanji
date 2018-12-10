from django.db import models
from authors.apps.authentication.models import User

# Create your models here.


class Articles(models.Model):
    """ Model for all articles """
    slug = models.SlugField(max_length=250, default='non')
    title = models.CharField(max_length=50, default='non')
    description = models.CharField(max_length=250, default='non')
    body = models.CharField(max_length=550, default='non')
    tagList = models.CharField(max_length=50,
                               default='non')  # ["dragons", "training"],
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    favorited = models.BooleanField(default=False)
    favoritesCount = models.IntegerField(default=0)
    readtime = models.IntegerField(default=0)
    author = models.ForeignKey(User, default=0, on_delete=models.CASCADE)

    def __str__(self):
        """ String representation of db object """
        return ' {}: {}'.format(self.id, self.slug)
