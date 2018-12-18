import logging
from django.db import models
from rest_framework.reverse import reverse

from authors.apps.authentication.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
from authors.apps.notifier.utils import Notifier
from authors.apps.profiles.models import Profile

logger = logging.getLogger(__name__)


class Articles(models.Model):
    """ Model for all articles """
    slug = models.SlugField(unique=True, max_length=250)
    title = models.CharField(max_length=250)
    description = models.CharField(max_length=350)
    body = models.TextField()
    tagList = models.CharField(max_length=200)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    favorited = models.BooleanField(default=False)
    favoritesCount = models.IntegerField(default=0)
    readtime = models.IntegerField(default=0)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-createdAt", "-updatedAt"]


# signal handlers
@receiver(post_save, sender=Articles)
def articles_notifications_handler(sender, **kwargs):
    # create a notification
    article = kwargs['instance']
    author = article.author.user
    profile = Profile.objects.get_or_create(user=author)
    profile = profile[0]

    followers = profile.get_followers().values('follower')
    qs = User.objects.filter(pk=None)
    for user in followers:
        u = User.objects.filter(pk=user['follower'])
        qs = Notifier.intersect_querysets(qs, u)

    url = reverse('articleSpecific', args=[article.slug, ])
    reverse_url = reverse('mailing-list-status')
    subject = "New Publication Notification"
    message = """
    %s published a new article.Check it out at %s .
    You are seeing this email because you are subscribed to /n
    receive email notifications.To unsubscribe from this emails
    login and unsubscribe by following %s
    """ % (author.email, url, reverse_url)

    Notifier.notify_multiple(actor=author,
                             recipients=qs,
                             action_object=article,
                             verb="published a new article",
                             message=message,
                             subject=subject
                             )
