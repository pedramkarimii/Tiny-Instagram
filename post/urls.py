from django.urls import path
from post.views import HomePostView, UpdatePostView, DeletePostView
# from django.views.generic import TemplateView
urlpatterns = [
    path('showposts/', HomePostView.as_view(), name='show_post'),
    # path("post/<int:pk>/update/", TemplateView.as_view(template_name='post/update_post.html'), name="show_delete_post"),
    path('post/<int:pk>/update/', UpdatePostView.as_view(), name='update_post'),
    path('post/<int:pk>/delete/', DeletePostView.as_view(), name='delete_post'),
]
