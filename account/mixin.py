from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from account.managers import UserManager
from django.db import models

from core.mixin import DeleteManagerMixin


class BaseModelUserMixin(AbstractBaseUser, PermissionsMixin):
    """
    Mixin class for user models.

    This class provides common fields and methods for user models. It is intended to be used
    as a mixin with other user models to avoid code duplication.

    Attributes:
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
        abstract (bool): Indicates that this is an abstract base class and not a concrete model.
        ordering (tuple): Specifies the default ordering of user records by update time and active status.
        verbose_name (str): Singular name for the model used in the admin interface.
        verbose_name_plural (str): Plural name for the model used in the admin interface.

    Methods:
        has_perm: Method to check if the user has a specific permission.
        has_module_perms: Method to check if the user has permissions for a specific module.
    """

    creat_time = models.DateTimeField(auto_now_add=True, editable=False)
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
        ordering = ['-update_time', 'is_deleted']
        verbose_name = 'user'
        verbose_name_plural = 'users'
