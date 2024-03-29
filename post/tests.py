from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Post, Comment, Vote

User = get_user_model()


class ModelsTestCase(TestCase):
    def setUp(self):
        # Create User Profiles
        self.user1 = User.objects.create(username='pedramkarimi', email='pedram.9060@gmail.com',
                                         phone_number='09128355747')
        self.user2 = User.objects.create_user(username="AliBaghani", email="ali@gmail.com", phone_number='09101234567')
        self.user3 = User.objects.create_user(username="HamidBalaghi", email="hamid@gmail.com",
                                              phone_number='09101234500')

        # Create Posts
        self.post1 = Post.objects.create(owner=self.user1.profile, title="first post",
                                         body="pedram")
        self.post2 = Post.objects.create(owner=self.user2.profile, title="hi",
                                         body="hi")
        self.post3 = Post.objects.create(owner=self.user3.profile, title="first post",
                                         body="hamid")

        # Add Comments
        # self.comment1_post1 = Comment.objects.create(owner=self.user2.profile, post=self.post1,
        #                                              comments="First comment on post 1.")
        # self.comment2_post1 = Comment.objects.create(owner=self.user3.profile, post=self.post1,
        #                                              comments="Second comment on post 1.", reply=self.comment1_post1)
        # self.comment1_post2 = Comment.objects.create(owner=self.user1.profile, post=self.post2,
        #                                              comments="First comment on post 2.")
        # self.comment2_post2 = Comment.objects.create(owner=self.user3.profile, post=self.post2,
        #                                              comments="Second comment on post 2.", reply=self.comment1_post2)
        # self.comment1_post3 = Comment.objects.create(owner=self.user1.profile, post=self.post3,
        #                                              comments="First comment on post 3.")
        # self.comment2_post3 = Comment.objects.create(owner=self.user2.profile, post=self.post3,
        #                                              comments="Second comment on post 3.", reply=self.comment1_post3)

        # Add Votes
        self.vote1_post1 = Vote.objects.create(user=self.user2, post=self.post1)
        self.vote2_post1 = Vote.objects.create(user=self.user3, post=self.post1)
        self.vote3_post1 = Vote.objects.create(user=self.user1, post=self.post1)
        self.vote1_post2 = Vote.objects.create(user=self.user1, post=self.post2)
        self.vote2_post2 = Vote.objects.create(user=self.user2, post=self.post2)
        self.vote3_post2 = Vote.objects.create(user=self.user3, post=self.post2)
        self.vote1_post3 = Vote.objects.create(user=self.user3, post=self.post3)
        self.vote2_post3 = Vote.objects.create(user=self.user1, post=self.post3)
        self.vote3_post3 = Vote.objects.create(user=self.user2, post=self.post3)

    def test_posts_and_likes(self):
        # List of all posts with their titles and the number of likes each post has
        posts_likes = {post.title: post.likes_count() for post in Post.objects.all()}
        self.assertEqual(posts_likes, {"First Post": 3, "Second Post": 3, "Third Post": 3})

    # def test_comments(self):
    #     # List of all comments with the username of the commenter and the post title
    #     comments_info = {comment.owner.user.username: comment.post.title for comment in Comment.objects.all()}
    #     self.assertEqual(comments_info, {
    #         "user2": "First Post",
    #         "user3": "First Post",
    #         "user1": "Second Post",
    #         "user3": "Second Post",
    #         "user1": "Third Post",
    #         "user2": "Third Post"
    #     })

    def test_votes(self):
        # List of all votes with the username of the voter and the post title
        votes_info = {vote.user.username: vote.post.title for vote in Vote.objects.all()}
        self.assertEqual(votes_info, {
            "user2": "First Post",
            "user3": "First Post",
            "user1": "First Post",
            "user1": "Second Post",
            "user2": "Second Post",
            "user3": "Second Post",
            "user3": "Third Post",
            "user1": "Third Post",
            "user2": "Third Post"
        })
