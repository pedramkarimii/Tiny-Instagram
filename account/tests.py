from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Profile, OptCode
User = get_user_model()


class ModelsTestCase(TestCase):
    """Test case for model creation and relationships."""

    def setUp(self):
        """Set up initial data for tests."""
        # Create a user object
        self.user = User.objects.create(username='pedramkarimi', email='pedram.9060@gmail.com',
                                        phone_number='09128355747')
        # Create a profile object associated with the user
        self.profile = Profile.objects.create(user=self.user, full_name='Pedram Karimi', name='pedram',
                                              last_name='karimi',
                                              gender='Female', age=30, bio='Hi',
                                              profile_picture='profile_picture/2024/03/17/d63d11b6-2ebc-46ea-9384-0a776f97e278_1pMrWIo.jpeg')
        # Create an OptCode object
        self.opt_code = OptCode.objects.create(code=1234, phone_number='09128355747')

    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(User.objects.count(), 1)

    def test_profile_creation(self):
        """Test profile creation."""
        self.assertEqual(Profile.objects.count(), 1)

    def test_opt_code_creation(self):
        """Test OptCode creation."""
        self.assertEqual(OptCode.objects.count(), 1)

    def test_user_profile_relationship(self):
        """Test relationship between User and Profile."""
        self.assertEqual(self.user.profile, self.profile)

    def test_opt_code_phone_number_uniqueness(self):
        """Test uniqueness of phone numbers in OptCode."""
        # Creating another OptCode object with the same phone number should raise an exception
        with self.assertRaises(Exception):
            OptCode.objects.create(code=1234, phone_number='09128355747')
