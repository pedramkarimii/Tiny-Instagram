from django.contrib.auth.models import BaseUserManager

""" 
Custom user manager for creating regular users, admin users, and superusers
"""


class UserManager(BaseUserManager):
    def create_user(self, phone_number, email, username, password):
        """
        Creates and saves a regular user with the given phone number, email, username, and password.
        """
        if not phone_number:
            raise ValueError('The phone number must be set')
        elif not email:
            raise ValueError('The Email must be set')
        elif not username:
            raise ValueError('The username must be set')
        user = self.model(phone_number=phone_number, email=self.normalize_email(email), username=username)
        user.is_admin = False
        user.is_superuser = False
        user.is_superuser = False
        user.set_password(password)
        user.save()
        return user

    def create_admin(self, phone_number, email, username, password):
        """
        Creates and saves an admin user with the given phone number, email, username, and password.
        """
        user = self.create_user(phone_number, email, username, password)
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = False
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, email, username, password):
        """
        Creates and saves a superuser with the given phone number, email, username, and password.
        """
        user = self.create_user(phone_number, email, username, password)
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.set_password(password)
        user.save()
        return user
