from django.urls import path
from post.views import HomePostView, UpdatePostView, DeletePostView, Explorer, CreatePostView, FollowUserView, \
    PostLikeView

"""
Defines URL patterns for post-related actions within the application.
- '/createpost/': Handles creating a new post.
- '/show_post/<int:pk>/': Displays a specific post.
- '/explorer/<int:pk>/': Displays explorer page.
- '/follow/<int:user_id>/': Handles following a user.
- '/unfollow/<int:user_id>/': Handles unfollowing a user.
- '/like/<int:post_id>/': Handles liking a post.
- '/post/<int:pk>/update/': Handles updating a post.
- '/post/<int:pk>/delete/': Handles deleting a post.
These URL patterns provide endpoints for creating, viewing, updating, and deleting posts, as well as exploring and 
interacting with other users' posts.
"""

urlpatterns = [
    path('createpost/', CreatePostView.as_view(), name='create_post'),
    path('show_post/<int:pk>/', HomePostView.as_view(), name='show_post'),
    path('explorer/<int:pk>/', Explorer.as_view(), name="explorer"),
    path('follow/<int:pk>/', FollowUserView.as_view(), name='follow_user'),
    path('like/<int:post_id>/', PostLikeView.as_view(), name='like_user'),
    path('post/<int:pk>/update/', UpdatePostView.as_view(), name='update_post'),
    path('post/<int:pk>/delete/', DeletePostView.as_view(), name='delete_post'),
]
