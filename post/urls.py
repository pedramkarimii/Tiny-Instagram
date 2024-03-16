from django.urls import path
from post.views import HomePostView, UpdatePostView, DeletePostView, Explorer, CreatePostView, UnfollowUserView, \
    FollowUserView

urlpatterns = [
    path('createpost/', CreatePostView.as_view(), name='create_post'),
    path('showposts/', HomePostView.as_view(), name='show_post'),
    path("explorer/", Explorer.as_view(), name="explorer"),

    path('follow/<int:user_id>/', FollowUserView.as_view(), name='follow_user'),
    path('unfollow/<str:user_id>/', UnfollowUserView.as_view(), name='unfollow_user'),

    path('post/<int:pk>/update/', UpdatePostView.as_view(), name='update_post'),
    path('post/<int:pk>/delete/', DeletePostView.as_view(), name='delete_post'),
]
