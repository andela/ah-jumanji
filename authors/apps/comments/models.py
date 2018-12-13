from django.db import models
from authors.apps.articles.models import Articles
from authors.apps.profiles.models import Profile

# Create your models here.


class Comment(models.Model):
    """ Implements comments class """
    body = models.CharField(max_length=350, default='comment')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    commenter = models.ForeignKey(Profile, on_delete=models.CASCADE)
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
