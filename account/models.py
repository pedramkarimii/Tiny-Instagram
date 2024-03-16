from django.db import models
from core.mixin import DeleteManagerMixin
from .mixin import BaseModelUserMixin
from django.urls import reverse
from ckeditor.fields import RichTextField

"""
          +-------------------+            1           +-------------------+
          |       User        |------------------------|      Profile      |
          +-------------------+          1             +-------------------+
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
    Model for users.

    This class represents a user model in the application. It extends the BaseModelUserMixin
    to inherit common functionalities related to user management.

    Attributes:
        email (EmailField): The email address of the user.
        phone_number (CharField): The phone number of the user.
        creat_time (DateTimeField): The timestamp indicating the creation time of the user record.
        update_time (DateTimeField): The timestamp indicating the last update time of the user record.
        is_deleted (BooleanField): Flag indicating whether the user has been deleted or not.
        is_active (BooleanField): Flag indicating whether the user is active or not.
        is_admin (BooleanField): Flag indicating whether the user has admin privileges.
        is_staff (BooleanField): Flag indicating whether the user is staff or not.
        is_superuser (BooleanField): Flag indicating whether the user is a superuser or not.
        USERNAME_FIELD (str): Field used for authentication, in this case, the phone number.
        REQUIRED_FIELDS (list): List of fields required for creating a user, in this case, email and full name.
        objects (UserManager): Custom manager for handling user queries.

    Meta:
        ordering (tuple): Specifies the default ordering of user records by update time and active status.
        verbose_name (str): Singular name for the model used in the admin interface.
        verbose_name_plural (str): Plural name for the model used in the admin interface.

    Methods:
        has_perm: Method to check if the user has a specific permission.
        has_module_perms: Method to check if the user has permissions for a specific module.

    Properties:
        title: Property that returns the full name of the user with each word capitalized.
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

    # def get_by_natural_key(self, username):
    #     return self.get(username=username)


class Profile(models.Model):
    """
    A model representing additional information associated with a user.

    Fields:
        user (OneToOneField): One-to-one relationship with the User model.
            If a User object is deleted, the associated Profile object will also be deleted.
            'related_name' attribute allows accessing Profile objects from a User instance using 'user.profile'.
        followers (ForeignKey): Relationship representing users who follow this profile.
        following (ForeignKey): Relationship representing users whom this profile follows.
        create_time_follow (DateTimeField): Creation time of the follow relationship.
            Automatically set to the current datetime when the object is first created.
        full_name (CharField): User's full name.
        name (CharField): User's first name.
        last_name (CharField): User's last name.
        gender (CharField): User's gender.
        age (PositiveSmallIntegerField): User's age.
        bio (RichTextField): User's biography.
        profile_picture (ImageField): User's profile picture.
        is_deleted (BooleanField): Flag indicating if the profile is deleted.
        is_active (BooleanField): Flag indicating if the profile is active.
        create_time (DateTimeField): Creation time of the profile.
            Automatically set to the current datetime when the object is first created.
        update_time (DateTimeField): Last update time of the profile.
            Automatically updated to the current datetime whenever the object is saved.

    Managers:
        objects (DeleteManagerMixin): Custom manager for handling profile queries.
            Implements soft deletion functionality.

    Meta:
        ordering: Specifies default ordering for queryset results.
        verbose_name: Human-readable name for a single object of the model.
        verbose_name_plural: Human-readable name for the model in plural form.
        constraints: Define constraints such as unique constraints.
        indexes: Define indexes for faster database query performance.

    Methods:
        __str__: Returns a string representation of the Profile object.
        get_absolute_url: Returns the absolute URL of the profile instance.
        capitalize (property): Returns the full name of the user with each word capitalized.
        get_follower_following: Gets the followers or following of a user based on a provided primary key.
        get_follower_following_count: Gets the count of followers and following
         of a user based on a provided primary key.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_query_name='user_profile')
    followers = models.ForeignKey(User, related_name='user_following', on_delete=models.CASCADE, null=True,
                                  blank=True)
    following = models.ForeignKey(User, related_name='user_followers', on_delete=models.CASCADE, null=True,
                                  blank=True)
    is_follow = models.BooleanField(default=False)
    create_time_follow = models.DateTimeField(auto_now_add=True, editable=False)
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
        ordering = ["-update_time"]
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

    def get_absolute_url(self):
        """Method to return the absolute URL of the profile instance."""
        return reverse("profile_detail", args=[self.id])

    @property
    def capitalize(self):
        """Property method that returns the full name of the user with each word capitalized."""
        return self.full_name.title()

    def get_follower_following(self, pk):
        """Method to get the followers of a user."""
        followers = self.followers.objects.get(pk=pk)
        following = self.following.objects.get(pk=pk)
        if followers and followers.is_active and not followers.exists():
            return followers
        elif following and following.is_active and not following.exists():
            return following
        else:
            return None

    def get_follower_following_count(self, pk):
        """Method to get the number of followers and following of a user."""
        followers = self.followers.objects.filter(pk=pk).count()
        following = self.following.objects.filter(pk=pk).count()
        return followers, following


class OptCode(models.Model):
    """
    Model to store OTP (One Time Password) codes.

    Fields:
        code (PositiveSmallIntegerField): The OTP code.
        phone_number (CharField): The phone number associated with the OTP.
            This field is unique to ensure each phone number has only one OTP.
        created (DateTimeField): The datetime when the OTP was created.
            Automatically set to the current datetime when the object is first created.

    Meta:
        ordering: Specifies default ordering for queryset results based on the creation time.
        verbose_name: Human-readable name for a single object of the model.
        verbose_name_plural: Human-readable name for the model in plural form.
        unique_together: Ensures the combination of code and phone number is unique.
        index_together: Specifies an index for faster lookup by code and phone number.
        constraints: Define constraints such as unique constraints.
        indexes: Define indexes for faster database query performance.

    Methods:
        __str__: Returns a string representation of the OTP object displaying code, phone number, and creation time.
    """
    code = models.PositiveSmallIntegerField()
    phone_number = models.CharField(max_length=11, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
        unique_together = ['code', 'phone_number']
        index_together = [['code', 'phone_number']]
        constraints = [
            models.UniqueConstraint(fields=['code', 'phone_number'], name='unique_code_phone_number')
        ]
        indexes = [
            models.Index(fields=['code', 'phone_number'], name='index_code_phone_number')
        ]

    def __str__(self):
        return f"OTP: {self.code} - Phone: {self.phone_number} - Created: {self.created.strftime('%Y-%m-%d %H:%M:%S')}"
