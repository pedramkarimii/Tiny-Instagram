from django.urls import path
from post.views import HomePostView, UpdatePostView, DeletePostView, Explorer, CreatePostView, FollowUserView, \
    PostLikeView, ReplyCommentView

"""
Defines URL patterns for the application.

Attributes:
- createpost/ (path): Maps to CreatePostView for creating a new post.
- show_post/<int:pk>/ (path): Maps to HomePostView for displaying a specific post.
- explorer/<int:pk>/ (path): Maps to Explorer for exploring posts.
- reply_comment/ (path): Maps to ReplyCommentView for replying to a comment.
- follow/<int:pk>/ (path): Maps to FollowUserView for following a user.
- like/<int:post_id>/ (path): Maps to PostLikeView for liking a post.
- post/<int:pk>/update/ (path): Maps to UpdatePostView for updating a post.
- post/<int:pk>/delete/ (path): Maps to DeletePostView for deleting a post.
"""

urlpatterns = [
    path('createpost/', CreatePostView.as_view(), name='create_post'),
    path('show_post/<int:pk>/', HomePostView.as_view(), name='show_post'),
    path('explorer/<int:pk>/', Explorer.as_view(), name="explorer"),
    path('reply_comment/', ReplyCommentView.as_view(), name='reply_comment'),
    path('follow/<int:pk>/', FollowUserView.as_view(), name='follow_user'),
    path('like/<int:post_id>/', PostLikeView.as_view(), name='like_user'),
    path('post/<int:pk>/update/', UpdatePostView.as_view(), name='update_post'),
    path('post/<int:pk>/delete/', DeletePostView.as_view(), name='delete_post'),
]
