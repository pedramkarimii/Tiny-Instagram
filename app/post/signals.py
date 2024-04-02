from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Image, Post


@receiver(post_save, sender=Post)
def create_image_for_post(sender, instance, created, **kwargs):
    """
    Signal receiver function to create an Image object for a Post instance with an image field.

    Args:
    sender: The model class.
    instance: The actual instance being saved.
    created: A boolean; True if a new record was created.
    **kwargs: Additional keyword arguments.
    """
    # if created and getattr(instance, 'image_field', None):
    #     Image.objects.create(post_image=instance, images=getattr(instance, 'image_field'))
    if created and getattr(instance, 'images', None):
        images = instance.images.all()  # Retrieve all related images
        for image in images:
            Image.objects.create(post_image=instance, images=image)
