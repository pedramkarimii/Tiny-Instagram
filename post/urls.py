from django.urls import path
from post.views import HomePostView, UpdatePostView, DeletePostView, Explorer, CreatePostView, UnfollowUserView, \
    FollowUserView, PostLikeView, PostDislikeView

urlpatterns = [
    path('createpost/', CreatePostView.as_view(), name='create_post'),
    path('show_post/<int:pk>/', HomePostView.as_view(), name='show_post'),
    path("explorer/<int:pk>/", Explorer.as_view(), name="explorer"),
    path('follow/<int:user_id>/', FollowUserView.as_view(), name='follow_user'),
    path('unfollow/<str:user_id>/', UnfollowUserView.as_view(), name='unfollow_user'),
    path('like/<str:post_id>/', PostLikeView.as_view(), name='like_user'),
    path('dislike/<str:post_id>/', PostDislikeView.as_view(), name='dislike_user'),

    path('post/<int:pk>/update/', UpdatePostView.as_view(), name='update_post'),
    path('post/<int:pk>/delete/', DeletePostView.as_view(), name='delete_post'),
]
