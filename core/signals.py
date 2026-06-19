from django.contrib.auth.models import User
from django.db.models.signals import post_save
from account.models import Profile
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):  # pylint: disable=unused-argument
    """Function to create a profile for a new user."""
    if kwargs["created"]:
        Profile.objects.create(user=kwargs["instance"])
