from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from account.managers import UserManager
from django.db import models
from core.mixin import DeleteManagerMixin


class BaseModelUserMixin(AbstractBaseUser, PermissionsMixin):
    """
    This is a mixin class intended to be used with Django models to provide basic user-related fields and
        functionalities. It extends Django's AbstractBaseUser and PermissionsMixin classes.

    Attributes:
    - create_time: A DateTimeField that stores the creation time of the user instance.
    - update_time: A DateTimeField that stores the last update time of the user instance.
    - is_deleted: A BooleanField indicating whether the user instance is marked as deleted.
    - is_active: A BooleanField indicating whether the user instance is active.
    - is_admin: A BooleanField indicating whether the user instance has admin privileges.
    - is_staff: A BooleanField indicating whether the user instance is staff.
    - is_superuser: A BooleanField indicating whether the user instance is a superuser.
    - USERNAME_FIELD: Specifies the field used as the unique identifier for authentication (in this case,
        'phone_number').
    - REQUIRED_FIELDS: Specifies the fields required when creating a user instance.
    - objects: The manager for querying user instances.
    - soft_delete: An instance of DeleteManagerMixin for soft deletion functionality.

    Meta:
    - abstract: Indicates that this model is intended to be used as a base class only and should not be directly
        instantiated.
    - ordering: Specifies the default ordering of user instances in queries.
    - verbose_name: Specifies a human-readable name for the model in singular form.
    - verbose_name_plural: Specifies a human-readable name for the model in plural form.
    - constraints: Defines constraints on fields, such as uniqueness constraints on 'username' and 'email'.
    - indexes: Defines indexes for optimizing database queries.
    """
    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    update_time = models.DateTimeField(auto_now=True, editable=False)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ['username', 'email']
    objects = UserManager()
    soft_delete = DeleteManagerMixin()

    class Meta:
        abstract = True
        ordering = ('-update_time', '-create_time', 'is_deleted')
        verbose_name = 'user'
        verbose_name_plural = 'users'
        constraints = [
            models.UniqueConstraint(fields=['username', 'email'], name='unique_username_email')
        ]
        indexes = [
            models.Index(fields=['username', 'email'], name='index_username_email')
        ]
