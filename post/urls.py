from django.urls import path
from post.views import HomePostView, UpdatePostView, DeletePostView, Explorer
urlpatterns = [
    path('showposts/', HomePostView.as_view(), name='show_post'),
    path("explorer/", Explorer.as_view(), name="explorer"),
    path('post/<int:pk>/update/', UpdatePostView.as_view(), name='update_post'),
    path('post/<int:pk>/delete/', DeletePostView.as_view(), name='delete_post'),
]
