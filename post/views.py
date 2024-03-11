from django.urls import reverse_lazy
# from account.models import User
from core.mixin import HttpsOptionMixin as CustomView
from post.forms import UpdatePostForm
from post.models import Post
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect


class HomePostView(CustomView):
    template_name = 'post/posts.html'
    http_method_names = ['get']

    def get(self, request):
        user = request.user
        posts = Post.objects.filter(owner=user.profile)
        return render(request, self.template_name, {'posts': posts})


class UpdatePostView(CustomView):
    """
    View for updating a post.
    """
    template_name = 'post/update_post.html'
    success_url = reverse_lazy('show_post')
    form_class = UpdatePostForm
    http_method_names = ['get', 'post']

    def get(self, request, pk):
        """
        Renders the form for updating a post.
        """
        post = Post.objects.get(pk=pk)
        form = self.form_class(instance=post)
        return render(request, self.template_name, {'form': form, 'post': post})

    def post(self, request, pk):
        """
        Processes the form submission for updating a post.
        """
        post = get_object_or_404(Post, pk=pk)
        form = self.form_class(request.POST, request.FILES, instance=post)
        if form.is_valid():
            print(form.cleaned_data)
            form.save()
            messages.success(request, 'Post updated successfully')
            return redirect(self.success_url)
        else:
            messages.error(request, 'Failed to update post. Please check the form.')
            return render(request, self.template_name, {'form': form})


class DeletePostView(CustomView):
    """
    View for deleting a post.
    """
    template_name = 'post/delete_post.html'
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('show_post')

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        return render(request, self.template_name, {'post': post})

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post:
            post.delete()
            messages.success(request, 'Post deleted successfully!')
            return redirect(self.success_url)
        else:
            messages.error(request, 'Post not found!')
            return redirect(self.success_url)
