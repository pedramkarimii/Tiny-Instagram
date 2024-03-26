from django.db import models
from core.mixin import DeleteManagerMixin
from .mixin import BaseModelUserMixin
from ckeditor.fields import RichTextField

"""
          +-------------------+            1           +-------------------+
          |       User        |------------------------|      Profile      |
          +-------------------+            1           +-------------------+
          | id                |<-----------------------| id                |
          | username          |                        | user_id     FK    |
          | email             |                        | followers_id      |
          | phone_number      |                        | following_id      |
          | create_time       |                        | create_time_follow|
          | update_time       |                        | full_name         |
          | is_deleted        |                        | name              |
          | is_active         |                        | last_name         |
          | is_admin          |                        | gender            |
          | is_staff          |                        | age               |
          | is_superuser      |                        | bio               |
          +-------------------+                        | profile_picture   |
                                                       | is_deleted        |
                                                       | is_active         |
                                                       | create_time       |
                                                       | update_time       |
                                                       +-------------------+
          +-------------------+
          |      OptCode      |
          +-------------------+
          | id                |
          | code              |
          | phone_number      |
          | created           |
          +-------------------+

"""


class User(BaseModelUserMixin):
    """
    Represents the User model which inherits from the BaseModelUserMixin.

    Attributes:
    - username (CharField): Specifies the username of the user.
    - email (EmailField): Specifies the email address of the user.
    - phone_number (CharField): Specifies the phone number of the user.

    Methods:
    - title: Property method that returns the title-cased version of the username.
    - __str__: Method to return a string representation of the User object.
    - followers_count: Method to return the number of followers for the user.
    - following_count: Method to return the number of users the user is following.
    """
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=11, unique=True)

    @property
    def title(self):
        return self.username.title()

    def __str__(self):
        """Method to return a string representation of the User object."""
        return self.username

    def followers_count(self):
        """Method to return the number of followers for a given user."""
        return self.user_followers.count()

    def following_count(self):
        """Method to return the number of following for a given user."""
        return self.user_following.count()


class Profile(models.Model):
    """
    Represents the Profile model.

    Attributes:
    - user (OneToOneField): Specifies the user associated with the profile.
    - full_name (CharField): Specifies the full name of the profile.
    - name (CharField): Specifies the name of the profile.
    - last_name (CharField): Specifies the last name of the profile.
    - gender (CharField): Specifies the gender of the profile.
    - age (PositiveSmallIntegerField): Specifies the age of the profile.
    - bio (RichTextField): Specifies the biography of the profile.
    - profile_picture (ImageField): Specifies the profile picture of the profile.
    - is_deleted (BooleanField): Indicates if the profile is deleted.
    - is_active (BooleanField): Indicates if the profile is active.
    - create_time (DateTimeField): Specifies the creation time of the profile.
    - update_time (DateTimeField): Specifies the last update time of the profile.

    Methods:
    - __str__: Method to return a string representation of the Profile object.
    - post_count: Method to return the count of posts associated with the profile.
    - capitalize: Property method that returns the full name of the user with each word capitalized.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_query_name='user_profile')
    full_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)
    age = models.PositiveSmallIntegerField(default=0)
    bio = RichTextField()
    profile_picture = models.ImageField(upload_to='profile_picture/%Y/%m/%d/')
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    update_time = models.DateTimeField(auto_now=True, editable=False)
    objects = DeleteManagerMixin()  # Assuming UserManager is a custom manager < soft delete >

    class Meta:
        ordering = ('-update_time', '-create_time')
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

        constraints = [
            models.UniqueConstraint(fields=['user', 'full_name'], name='unique_user_full_name')
        ]
        indexes = [
            models.Index(fields=['user', 'full_name'], name='index_user_full_name')
        ]

    def __str__(self):
        """Method to return a string representation of the Profile object."""
        return self.full_name

    def post_count(self):
        """
        Method to return the count of posts associated with the profile.
        """
        return self.posts.count()

    @property
    def capitalize(self):
        """Property method that returns the full name of the user with each word capitalized."""
        return self.full_name.title()


class Relation(models.Model):
    """
    Represents the Relation model.

    Attributes:
    - followers (ForeignKey): Specifies the user who is following.
    - following (ForeignKey): Specifies the user who is being followed.
    - is_follow (BooleanField): Indicates whether the relationship is a follower-following connection.
    - create_time_follow (DateTimeField): Specifies the timestamp when the relationship was created.

    Methods:
    - __str__: Method to return a string representation of the Relation object.
    """
    followers = models.ForeignKey(User, related_name='user_following', on_delete=models.CASCADE, null=True,
                                  blank=True)
    following = models.ForeignKey(User, related_name='user_followers', on_delete=models.CASCADE, null=True,
                                  blank=True)
    is_follow = models.BooleanField(default=False)
    create_time_follow = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        """Method to return a string representation of the Relation object."""
        return f"{self.followers} - {self.following}"

    class Meta:
        ordering = ('-create_time_follow',)
        verbose_name = 'Relation'
        verbose_name_plural = 'Relations'
        constraints = [
            models.UniqueConstraint(fields=['followers', 'following'], name='unique_followers_following')
        ]
        indexes = [
            models.Index(fields=['followers', 'following'], name='index_followers_following')
        ]


class OptCode(models.Model):
    """
    Represents the OptCode model.

    Attributes:
    - code (PositiveSmallIntegerField): Stores the OTP code.
    - phone_number (CharField): Stores the phone number associated with the OTP.
    - email (EmailField): Stores the email associated with the OTP (optional).
    - created (DateTimeField): Specifies the timestamp when the OTP was created.
    - is_used (BooleanField): Indicates whether the OTP has been used.

    Methods:
    - __str__: Method to return a string representation of the OptCode object, including code, phone number, and
        creation time.
    """
    code = models.PositiveSmallIntegerField()
    phone_number = models.CharField(max_length=11, unique=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ('created',)
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        constraints = [
            models.UniqueConstraint(fields=['code', 'phone_number'], name='unique_code_phone_number')
        ]
        indexes = [
            models.Index(fields=['code', 'phone_number'], name='index_code_phone_number')
        ]

    def __str__(self):
        """
        Method to return a string representation of the OptCode object including code, phone number, and creation time.
        """
        return f"OTP: {self.code} - Phone: {self.phone_number} - Created: {self.created.strftime('%Y-%m-%d %H:%M:%S')}"
