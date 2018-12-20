import logging

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.reverse import reverse

from authors.apps.articles.models import Articles
from authors.apps.favourite.models import Favourite
from authors.apps.profiles.models import Profile
from authors.apps.notifier.utils import Notifier

# Create your models here.
logger = logging.getLogger(__file__)


class Comment(models.Model):
    """ Implements comments class """
    body = models.CharField(max_length=350, default='comment')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    commenter = models.ForeignKey(Profile, on_delete=models.CASCADE)
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)


@receiver(post_save, sender=Comment)
def comments_notifications_handler(sender, created, **kwargs):
    """notify all people who have favourited an article """
    if created:
        logger.info("Notification for comment creation")
        comment = kwargs['instance']
        logger.debug(comment)
        favourites = Favourite.objects.filter(article=comment.article)
        # notify favouriters if they exist
        if len(favourites) > 0:
            fav = favourites[0]
            recipients = fav.get_favouriters()

            url = reverse('articleSpecific', args=[comment.article.slug, ])
            reverse_url = reverse('mailing-list-status')
            subject = "New Publication Comment Notification"
            message = """
                %s commented on an  article you favourited.Check it out at %s .

                You are seeing this email because you are subscribed to /n
                receive email notifications.To unsubscribe from this emails
                login and unsubscribe by following %s

                """ % (comment.commenter.user.email, url, reverse_url)

            Notifier.notify_multiple(
                actor=comment.commenter,
                action_object=comment.article,
                verb="Commented on the article",
                recipients=recipients,
                message=message,
                subject=subject
            )
        else:
            logger.debug("No Notifications made for comment %s" % comment)
