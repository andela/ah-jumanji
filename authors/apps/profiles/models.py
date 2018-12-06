from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Local imports
from ..authentication.models import User

# Create your models here.


class Profile(models.Model):
    """
        Models a user's profile.
        Is an extension of app's User model
    """
    # Link profile to a User thro one-to-one rlship
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)

    # Add fields onto `Profile` model
    username = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    full_name = models.CharField(max_length=50, blank=True)
    bio = models.CharField(max_length=200, blank=True)
    image = models.URLField(blank=True)
    country = models.CharField(max_length=3, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        """
            Schema for representation of a Profile object in Terminal
        """
        return self.email


# Recieve a signal whenever a User is created
# and initialize a Profile tied to the User
@receiver(post_save, sender=User)
def init_profile(sender, instance, created, **kwargs):
    """
        Initialize a `Profile` whenever an
        instance of a `User` is initialized
    """
    if created:
        Profile.objects.create(
            user=instance, username=instance.username, email=instance.email)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
        Save the profile initialized above
        if User is saved
    """
    instance.profile.save()
