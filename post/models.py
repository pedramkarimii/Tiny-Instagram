from ckeditor.fields import RichTextField
from django.db import models
from account.models import Profile, User
from core.mixin import DeleteManagerMixin

"""
   +--------------+         +----------------+         +-----------+
   |    Post      |         |    Comment     |         |    Vote   |
   +--------------+         +----------------+         +-----------+
   | id           |<--------| id             |<--------| id        |
   | owner_id (FK)|         | post_id (FK)   |         | user_id   |
   | body         |         | owner_id (FK)  |         | post_id   |
   | post_picture |         | reply_id (FK)  |         | created   |
   | title        |         | is_reply       |         +-----------+
   | is_deleted   |         | comments       |
   | is_active    |         | is_deleted     |
   | delete_time  |         | delete_time    |
   | create_time  |         | create_time    |
   | update_time  |         | update_time    |
   +--------------+         +----------------+

"""


class Post(models.Model):
    """
    Defines the Post model representing user posts in the application.
    Fields:
    - owner: ForeignKey to the Profile model representing the owner of the post.
    - body: RichTextField containing the content of the post.
    - post_picture: ImageField for uploading post pictures.
    - title: CharField for the title of the post.
    - is_deleted: BooleanField indicating if the post is deleted.
    - is_active: BooleanField indicating if the post is active.
    - delete_time: DateTimeField indicating the time when the post was deleted.
    - create_time: DateTimeField indicating the time when the post was created.
    - update_time: DateTimeField indicating the time when the post was last updated.
    - objects: Custom manager for soft deletion.

    Methods:
    - __str__: Returns a string representation of the Post object.
    - likes_count: Returns the number of likes (votes) on the post.
    - comments_count: Returns the number of comments on the post.

    Meta:
    - ordering: Specifies the default ordering of Post objects.
    - verbose_name: Sets the display name for a single Post object.
    - verbose_name_plural: Sets the display name for multiple Post objects.
    - get_latest_by: Specifies the field to use for retrieving the latest Post object.
    - indexes: Defines indexes for owner and title fields.
    """
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='posts')
    body = RichTextField()
    post_picture = models.ImageField(upload_to='post_picture/%Y/%m/%d/')
    title = models.CharField(max_length=255)
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
        indexes = [
            models.Index(fields=['owner', 'title'], name='index_owner_title_posts')
        ]

    def likes_count(self):
        """
        Defines the likes_count method of the Post model.
        This method returns the number of likes (votes) on the post.

        Returns:
        - Integer representing the count of likes (votes) on the post.
        """
        return self.post_vote.count()

    def comments_count(self):
        """
        Defines the comments_count method of the Post model.
        This method returns the number of comments on the post.

        Returns:
        - Integer representing the count of comments on the post.
        """
        return self.post_comments.count()


class Comment(models.Model):
    """
    Defines the Comment model which represents comments made by users on posts.
    Fields:
    - owner: ForeignKey to the Profile model representing the user who made the comment.
    - post: ForeignKey to the Post model representing the post on which the comment is made.
    - reply: ForeignKey to self representing a reply to another comment (optional).
    - is_reply: BooleanField indicating whether the comment is a reply to another comment.
    - comments: RichTextField containing the content of the comment.
    - is_deleted: BooleanField indicating whether the comment has been deleted.
    - delete_time: DateTimeField indicating the time when the comment was deleted.
    - create_time: DateTimeField indicating the time when the comment was created.
    - update_time: DateTimeField indicating the time when the comment was last updated.

    Methods:
    - __str__: Returns a string representation of the Comment object.

    Meta:
    - ordering: Specifies the default ordering of Comment objects.
    - verbose_name: Sets the display name for a single Comment object.
    - verbose_name_plural: Sets the display name for multiple Comment objects.
    - get_latest_by: Specifies the field to use for retrieving the latest Comment object.
    - constraints: Defines constraints for uniqueness of owner, post, and comments fields.
    - indexes: Defines indexes for owner and post fields.
    """
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, related_name='reply_comments', blank=True,
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
        constraints = [
            models.UniqueConstraint(fields=['owner', 'post', 'comments'], name='unique_owner_post_comments')
        ]
        indexes = [
            models.Index(fields=['owner', 'post'], name='index_owner_post_comments')
        ]


class Vote(models.Model):
    """
    Defines the Vote model which represents votes made by users on posts.
    Fields:
    - user: ForeignKey to the User model representing the user who made the vote.
    - post: ForeignKey to the Post model representing the post on which the vote is made.
    - create_time: DateTimeField indicating the time when the vote was created.

    Methods:
    - __str__: Returns a string representation of the Vote object.

    Meta:
    - ordering: Specifies the default ordering of Vote objects.
    - verbose_name: Sets the display name for a single Vote object.
    - verbose_name_plural: Sets the display name for multiple Vote objects.
    - get_latest_by: Specifies the field to use for retrieving the latest Vote object.
    - constraints: Defines constraints for uniqueness of user and post fields.
    - indexes: Defines indexes for user and post fields.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_vote')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_vote')
    create_time = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f'{self.user} - {self.post}'

    class Meta:
        ordering = ('-create_time',)
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'
        get_latest_by = '-create_time'
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_user_post_vote')
        ]
        indexes = [
            models.Index(fields=['user', 'post'], name='index_user_post_vote')
        ]
