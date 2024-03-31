from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Image, Post


@receiver(post_save, sender=Post)
def create_image_for_post(sender, instance, created, **kwargs):
    if created and getattr(instance, 'image_field', None):
        Image.objects.create(post_image=instance, images=getattr(instance, 'image_field'))
