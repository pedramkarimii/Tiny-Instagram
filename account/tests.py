from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Profile, OptCode

User = get_user_model()


class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', email='test@example.com', phone_number='1234567890')
        self.profile = Profile.objects.create(user=self.user, full_name='Test User', name='Test', last_name='User',
                                              gender='Male', age=25, bio='Test bio', profile_picture='test.jpg')
        self.opt_code = OptCode.objects.create(code=123456, phone_number='1234567890')

    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 1)

    def test_profile_creation(self):
        self.assertEqual(Profile.objects.count(), 1)

    def test_opt_code_creation(self):
        self.assertEqual(OptCode.objects.count(), 1)

    def test_user_profile_relationship(self):
        self.assertEqual(self.user.profile, self.profile)

    def test_opt_code_phone_number_uniqueness(self):
        with self.assertRaises(Exception):
            OptCode.objects.create(code=654321,
                                   phone_number='1234567890')  # Attempt to create OptCode with duplicate phone number
