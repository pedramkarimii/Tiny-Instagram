from django.contrib.auth import get_user_model
from django.test import TestCase
from app.account.models import Profile
from .models import Post, Image, Comment, Vote, CommentLike

User = get_user_model()


class ModelsTestCase(TestCase):
    def setUp(self):
        """Setting up initial data for testing"""
        self.user = User.objects.create(username='pedramkarimi', email='pedram.9060@gmail.com',
                                        phone_number='09128355747')
        self.profile = Profile.objects.create(user=self.user, full_name='Pedram Karimi', name='pedram',
                                              last_name='karimi',
                                              gender='Female', age=30, bio='Hi',
                                              profile_picture='profile_picture/2024/03/17/d63d11b6-2ebc-46ea'
                                                              '-9384-0a776f97e278_1pMrWIo.jpeg')
        self.post = Post.objects.create(owner=self.profile, body="Test Body", title="Test Title")
        self.image = Image.objects.create(post_image=self.post, images="test_image.jpg")
        self.comment = Comment.objects.create(owner=self.profile, post=self.post, comments="Test Comment")
        self.vote = Vote.objects.create(user=self.user, post=self.post)
        self.comment_like = CommentLike.objects.create(user=self.user, comment=self.comment)

    def test_post_model(self):
        """Test if post model attributes are correctly set"""
        self.assertEqual(self.post.owner, self.profile)
        self.assertEqual(self.post.body, "Test Body")
        self.assertEqual(self.post.title, "Test Title")
        self.assertFalse(self.post.is_deleted)
        self.assertTrue(self.post.is_active)

    def test_image_model(self):
        """Test if image model attributes are correctly set"""
        self.assertEqual(self.image.post_image, self.post)
        self.assertEqual(self.image.images, "test_image.jpg")
        self.assertFalse(self.image.is_deleted)
        self.assertTrue(self.image.is_active)

    def test_comment_model(self):
        """Test if comment model attributes are correctly set"""
        self.assertEqual(self.comment.owner, self.profile)
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.comments, "Test Comment")
        self.assertTrue(self.comment.is_active)
        self.assertFalse(self.comment.is_deleted)

    def test_vote_model(self):
        """Test if vote model attributes are correctly set"""
        self.assertEqual(self.vote.user, self.user)
        self.assertEqual(self.vote.post, self.post)

    def test_comment_like_model(self):
        """Test if comment like model attributes are correctly set"""
        self.assertEqual(self.comment_like.user, self.user)
        self.assertEqual(self.comment_like.comment, self.comment)
