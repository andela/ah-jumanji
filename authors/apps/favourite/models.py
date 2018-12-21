"""
    Models for Favourite app
"""
import logging

from django.contrib.auth import get_user_model
from django.db import models

# local imports
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.reverse import reverse

from authors.apps.articles.models import Articles
from authors.apps.authentication.models import User
from authors.apps.notifier.utils import Notifier
from authors.apps.profiles.models import Profile

logger = logging.getLogger(__file__)


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

    def get_favouriters(self):
        """
        Reuturn users who have favourited an article
        :return:
        """
        article = self.article
        favourites = Favourite.objects.filter(article=article, favourite=1)
        favouriters = favourites.values('user')
        # get a null queryset and append users to it
        user = get_user_model()
        users = user.objects.filter(pk=None)
        for favouriter in favouriters:
            logger.debug(favouriter)
            u = user.objects.filter(pk=favouriter['user'])
            users = Notifier.intersect_querysets(users, u)
        # return a queryset of users
        return users


@receiver(post_save, sender=Favourite)
def fovourites_notifications_handler(sender, created, **kwargs):
    """Notify the author when their article is favourited"""
    instance = kwargs['instance']
    if created:
        logger.debug("article %s has been favourited by %s" % (
            instance.article, instance.user))

        url = reverse('articleSpecific', args=[instance.article.slug, ])
        reverse_url = reverse('mailing-list-status')

        subject = "New Article favourite Notification"
        Message = """
        Your article %s has been favourited by %s.
        You are seeing this email because you are subscribed to /n
                receive email notifications.To unsubscribe from this emails
                login and unsubscribe by following %s
        """ % (url, instance.user.username, reverse_url)

        Notifier.notify_multiple(
            actor=instance.user,
            action_object=instance.article,
            verb="Commented on the article",
            recipients=User.objects.filter(pk=instance.user.pk),
            message=Message,
            subject=subject
        )
