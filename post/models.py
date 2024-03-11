from ckeditor.fields import RichTextField
from django.db import models
from account.models import Profile, User
from core.mixin import DeleteManagerMixin

from django.urls import reverse


class Post(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, )
    body = RichTextField()
    post_picture = models.ImageField(upload_to='post_picture/%Y/%m/%d/')
    title = models.SlugField(max_length=100, unique=True, editable=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    delete_time = models.DateTimeField(auto_now=True, editable=False)
    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    update_time = models.DateTimeField(auto_now=True, editable=False)
    objects = DeleteManagerMixin()  # Assuming UserManager is a custom manager < soft delete >

    def __str__(self):
        return f'{self.owner} - {self.title} - {self.update_time}'

    class Meta:
        ordering = ['-create_time']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        get_latest_by = 'create_time'
        constraints = [
            models.UniqueConstraint(fields=['owner', 'title'], name='owner_slug_unique'),
        ]

    def get_absolute_url(self):
        return reverse('show_post', args={self.id, self.title})
