from ckeditor.fields import RichTextField
from django.db import models
from account.models import Profile, User
from core.mixin import DeleteManagerMixin

"""
+------------------+             +-------------------+              +----------------+
|     Profile      |    1       *|        Post       |      *       |     Comment    |
+------------------+-------------+-------------------+--------------+----------------+
| id               |<------------| owner_id (FK)     |              | id             |
|                  |             | body              |              | owner_id (FK)  |
|                  |             | post_picture      |              | post_id (FK)   |
|                  |             | title             |              | reply_id (FK)  |
|                  |             | is_deleted        |              | body           |
|                  |             | is_active         |              | is_deleted     |
+------------------+             | delete_time       |              | delete_time    |
                                 | create_time       |              | create_time    |
                                 | update_time       |              | update_time    |
                                 +-------------------+              +----------------+

"""


class Post(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_query_name='posts')
    body = RichTextField()
    post_picture = models.ImageField(upload_to='post_picture/%Y/%m/%d/')
    title = models.CharField(max_length=255)
    likes = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='post_likes', null=True, blank=True)
    dislikes = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='post_dislikes', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    delete_time = models.DateTimeField(auto_now=True, editable=False)
    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    update_time = models.DateTimeField(auto_now=True, editable=False)
    objects = DeleteManagerMixin()  # Assuming UserManager is a custom manager < soft delete >

    def __str__(self):
        return f'{self.owner} - {self.title} - {self.update_time}'

    class Meta:
        ordering = ('-update_time', '-create_time')
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        get_latest_by = '-create_time'


class Comment(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_query_name='user_comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_query_name='posta_comments')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, related_query_name='reply_comments', blank=True,
                              null=True)
    is_reply = models.BooleanField(default=False)
    comments = RichTextField()
    is_deleted = models.BooleanField(default=False)
    delete_time = models.DateTimeField(auto_now=True, editable=False)
    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    update_time = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f'{self.owner} - {self.post} - {self.update_time}'

    class Meta:
        ordering = ('-update_time', '-create_time')
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        get_latest_by = '-create_time'
