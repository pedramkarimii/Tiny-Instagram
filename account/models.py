from django.db import models
from core.mixin import DeleteManagerMixin
from .mixin import BaseModelUserMixin
from django.urls import reverse
from ckeditor.fields import RichTextField

"""
Explanation:
- User model:
  - Represents users in the system.
  - It has a one-to-one relationship with the Profile model via the user_id foreign key.
  - Attributes:
    - id (PK): Primary Key uniquely identifying each user.
    - username: Username of the user.
    - email: Email address of the user.
    - phone_number: Phone number of the user.

- Profile model:
  - Stores additional information associated with a user.
  - It has a one-to-one relationship with the User model via the user_id foreign key.
  - Attributes:
    - user_id (FK): Foreign Key referencing the corresponding User instance.
    - full_name: Full name of the user.
    - name: First name of the user.
    - last_name: Last name of the user.
    - bio: Biography or additional information about the user.
    - image: Image associated with the user's profile.
    - create_time: Timestamp indicating the creation time of the profile.
    - update_time: Timestamp indicating the last update time of the profile.

- OptCode model:
  - Represents OTP codes associated with phone numbers.
  - No direct relationship with the User or Profile model.
  - Attributes:
    - id (PK): Primary Key uniquely identifying each OTP code.
    - code: The OTP code.
    - phone_number: Phone number associated with the OTP code.
    - created: Timestamp indicating the creation time of the OTP code.

      +-------------------+        +-------------------+          +-------------------+
      |        User       |        |      Profile      |          |      OptCode      |
      +-------------------+        +-------------------+          +-------------------+
      | id (PK)           |1      1| user_id (FK)      |1       1 | id (PK)           |
      | username          |<------>| full_name         |<-------->| code              |
      | email             |        | name              |          | phone_number      |
      | phone_number      |        | last_name         |          | created           |
      |                   |        | bio               |          |                   |
      |                   |        | profile_picture   |          |                   |
      |                   |        | create_time       |          |                   |
      |                   |        | update_time       |          |                   |
      +-------------------+        +-------------------+          +-------------------+

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

    def get_by_natural_key(self, username):
        return self.get(username=username)

class Profile(models.Model):
    """
    Model representing additional information associated with a user.

    user: One-to-one relationship with the User model.
    If a User object is deleted, the associated Profile object will also be deleted.
    'related_name' attribute allows accessing Profile objects from a User instance using 'user.profile'.

    full name: Field to store the user's full name

    name: Field to store the user's first name

    last name: Field to store the user's last name

    age: Field to store the user's age

    address: Field to store the user's address

    profile_picture:  Field to store the user's profile picture.

    create time: Field to store the creation time of the profile.
    'auto_now_add=True' automatically sets the field to the current datetime when the object is first created.
    'editable=False' prevents this field from being edited.

   update time: Field to store the last update time of the profile.
   'auto_now=True' automatically updates the field to the current datetime whenever the object is saved.
   'editable=False' prevents this field from being edited.

   objects: Custom manager for handling profile queries.
   manager (DeleteManagerMixin): Custom manager mixin for soft deletion functionality.

   """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
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
        unique_together = ['user', 'full_name']
        index_together = [['user', 'full_name']]
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


class OptCode(models.Model):
    """
    Model for otp codes.
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
