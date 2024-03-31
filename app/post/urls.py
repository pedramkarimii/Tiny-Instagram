from django.urls import path
from app.post.views import HomePostView, UpdatePostView, DeletePostView, Explorer, CreatePostView, FollowUserView, \
    PostLikeView, PostDetailView, ReplyCommentView, DeleteCommentView, CommentLikeView, ReplyCommentLike

"""
Defines URL patterns for the application.

Attributes:
- createpost/ (path): Maps to CreatePostView for creating a new post.
- show_post/<int:pk>/ (path): Maps to HomePostView for displaying a specific post.
- post_detail/<int:pk>/ (path): Maps to PostDetailView for displaying a specific post and comments.
- explorer/<int:pk>/ (path): Maps to Explorer for exploring posts.
- comment/<int:pk>/reply/ (path): Maps to ReplyCommentView for replying to a comment.
- follow/<int:pk>/ (path): Maps to FollowUserView for following a user.
- like/<int:post_id>/ (path): Maps to PostLikeView for liking a post.
- like/<int:post_id>/<int:comment_id>/ (path): Maps to CommentLikeView for liking a comment.
- like/<int:post_id>/<int:comment_id>/ (path): Maps to ReplyCommentLikeView for liking a reply comment.
- comment/<int:pk>/reply/ (path): Maps to ReplyCommentView for replying to a comment.
- comment/<int:pk>/delete/ (path): Maps to DeleteCommentView for deleting a comment.
- post/<int:pk>/update/ (path): Maps to UpdatePostView for updating a post.
- post/<int:pk>/delete/ (path): Maps to DeletePostView for deleting a post.
"""

urlpatterns = [
    path('createpost/', CreatePostView.as_view(), name='create_post'),
    path('explorer/', Explorer.as_view(), name="explorer"),
    path('show_post/<int:pk>/', HomePostView.as_view(), name='show_post'),
    path('comment/<int:pk>/reply/', ReplyCommentView.as_view(), name='reply_comment'),
    path('comment/<int:pk>/delete/', DeleteCommentView.as_view(), name='delete_comment'),
    path('post_detail/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('follow_user/<int:user_id>/<int:post_id>/', FollowUserView.as_view(), name='follow_user'),
    path('like/<int:post_id>/', PostLikeView.as_view(), name='like_user'),
    path('like/<int:post_id>/<int:comment_id>/', CommentLikeView.as_view(), name='like_comment'),
    path('like/<int:post_id>/<int:comment_id>/<int:reply_comment_id>/', ReplyCommentLike.as_view(),
         name='like_reply_comment'),
    path('post/<int:pk>/update/', UpdatePostView.as_view(), name='update_post'),
    path('post/<int:pk>/delete/', DeletePostView.as_view(), name='delete_post'),
]
