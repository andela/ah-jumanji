# Create your models here.
from django.contrib.auth import get_user_model
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
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    bio = models.CharField(max_length=200, blank=True)
    profile_photo = models.URLField(blank=True)
    country = models.CharField(max_length=3, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    twitter_handle = models.CharField(max_length=15, blank=True)
    website = models.URLField(blank=True)

    created = models.DateTimeField(
        auto_now_add=True,
        help_text="This is the time of creation of this record"
    )
    modified = models.DateTimeField(
        auto_now=True,
        help_text="This field is updated "
                  "any time this record is updated"
    )

    def __str__(self):
        """
            Schema for representation of a Profile object in Terminal
        """
        return self.email

    def get_followers(self):
        """get all users that follow a user"""
        followers = Following.objects.filter(followed=self.user)
        return followers

    def get_followed(self):
        """
        get all users that a user follows
        :return queryset:
        """
        followed = Following.objects.filter(follower=self.user)
        return followed

    def is_follower(self, usr):
        """
        check if user follows another user
        :param usr:
        :return bool:
        """
        for follows in self.get_followers():
            if follows.follower == usr:
                return True
        return False

    def is_followed(self, usr):
        """
        check if user is followed by a particular user
        :param usr:
        :return bool:
        """
        for follows in self.get_followed():
            if follows.followed == usr:
                return True
        return False


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
            user=instance,
            first_name=instance.username,
            username=instance.username)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
        Save the profile initialized above
        if User is saved
    """
    instance.profile.save()


class Following(models.Model):
    follower = models.ForeignKey(
        get_user_model(),
        related_name="relationship_creator",
        on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        get_user_model(),
        related_name="followed_user",
        on_delete=models.CASCADE
    )

    created = models.DateTimeField(
        auto_now_add=True,
        help_text="This is the time of creation of this record"
    )
    modified = models.DateTimeField(
        auto_now=True,
        help_text="This field is updated any time this record is updated"
    )
