from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse_lazy
from account.models import User, Profile
from core.mixin import HttpsOptionMixin as CustomView
from post.forms import UpdatePostForm, CreatCommentForm
from post.models import Post, Comment
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

class HomePostView(CustomView):
    template_name = 'post/posts.html'
    http_method_names = ['get', 'post']
    form_class = CreatCommentForm

    def get_success_url(self):
        return reverse_lazy('show_post', kwargs={'pk': self.kwargs['pk']})

    def get(self, request, pk):
        user = request.user
        posts = Post.objects.filter(owner=user.profile).order_by('-update_time', 'create_time')
        return render(request, self.template_name, {'posts': posts, 'form': self.form_class()})

    def post(self, request, pk):
        form = self.form_class(request.POST)
        if form.is_valid():
            post_instance = get_object_or_404(Post, pk=pk, owner=request.user.profile)
            comment = form.save(commit=False)
            comment.owner = request.user.profile
            comment.post = post_instance
            comment.save()
            messages.success(request, "You have created a new comment")
            return redirect(self.get_success_url())  # Redirect to dynamically obtained success URL

        # If form is not valid, render the form again with errors
        posts = Post.objects.filter(owner=request.user.profile).order_by('-update_time', 'create_time')
        return render(request, self.template_name, {'posts': posts, 'form': form})


class Explorer(CustomView):
    template_name = 'explorer/explorer.html'
    http_method_names = ['get']
    from_class = CreatCommentForm

    def get(self, request):

        users_with_profiles = User.objects.filter(is_active=True).prefetch_related('profile').order_by('update_time',
                                                                                                       'creat_time')
        user_posts = []
        for user in users_with_profiles:
            if hasattr(user, 'profile'):
                user_posts.append({
                    'user': user,
                    'posts': Post.objects.filter(owner=user.profile, is_deleted=False).order_by('-update_time',
                                                                                                'create_time').annotate(
                        num_likes=Count('likes'),
                        num_dislikes=Count('dislikes')
                    )
                })
        return render(request, self.template_name, {'user_posts': user_posts, 'form': self.from_class})


# class CreatCommentView(CustomView):
#     template_name = 'explorer/explorer.html'
#     success_url = reverse_lazy('explorer')
#     http_method_names = ['get', 'post']
#     form_class = CreatCommentForm
#
#     def get(self, request, *args, **kwargs):
#         # Handle GET requests here if needed
#         return redirect(self.success_url)
#
#     def post(self, request, *args, **kwargs):
#         user_id = kwargs.get('user_id')
#         post_id = kwargs.get('post_id')
#         comment_text = request.POST.get('comment')
#         post = Post.objects.get(pk=post_id)
#         user = User.objects.get(pk=user_id)
#         comment = Comment.objects.create(owner=user.profile, post=post, comment=comment_text)
#         comment.save()
#         messages.success(request, f"You have commented on {post.title}")
#         return redirect(self.success_url)


class FollowUserView(CustomView):
    template_name = 'explorer/explorer.html'
    success_url = reverse_lazy('explorer')
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        # Handle GET requests here if needed
        return redirect(self.success_url)

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        profile = Profile.objects.get(pk=user_id)
        current_user_profile = request.user.profile

        # Logic to follow the user
        current_user_profile.following = profile.user
        current_user_profile.save()

        # Add a success message
        messages.success(request, f"You are now following {profile.full_name}")

        return redirect(self.success_url)


class UnfollowUserView(CustomView):
    template_name = 'explorer/explorer.html'
    success_url = reverse_lazy('explorer')
    http_method_names = ['get', 'post']

    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(followers=request.uer, following=user)
        if profile.exists():
            messages.error(request, f"You are already following {user.username}")
        else:
            messages.success(request, f"You are following {user.username}")
            Profile.objects.create(followers=request.user, following=user)
        return redirect(self.success_url, user.id)

    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(followers=request.user, following=user)
        if profile.exists():
            profile.delete()
            messages.success(request, f"You have unfollowed {user.username}")
            return redirect(self.success_url)
        else:
            messages.error(request, f"You are not following {user.username}")
            return redirect(self.success_url, user.id)


class CreatePostView(LoginRequiredMixin, CustomView):
    template_name = 'post/create_post.html'
    success_url = reverse_lazy('show_post')
    form_class = UpdatePostForm
    http_method_names = ['get', 'post']

    def get(self, request):
        form = self.form_class()  # Assuming you have a PostForm defined
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = Profile.objects.get(user=request.user)
            if 'post_picture' in request.FILES:
                post.post_picture = request.FILES['post_picture']
                post.save()
                messages.success(request, 'Post created successfully!')
                return redirect(self.success_url)
            else:
                post.save()
                messages.success(request, 'Post created successfully!')
                return render(request, self.template_name, {'form': form}) and redirect(self.success_url)

        else:
            return render(request, self.template_name, {'form': form})


class UpdatePostView(CustomView):
    """
    View for updating a post.
    """
    template_name = 'post/update_post.html'
    success_url = reverse_lazy('show_post')
    form_class = UpdatePostForm
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.post_instance = get_object_or_404(Post, pk=self.kwargs['pk'])  # noqa

    def get(self, request, pk):  # noqa
        """
        Renders the form for updating a post.
        """
        post = self.post_instance
        form = self.form_class(instance=post)
        return render(request, self.template_name, {'form': form, 'post': post})

    def post(self, request, pk):  # noqa
        """
        Processes the form submission for updating a post.
        """
        post = self.post_instance
        form = self.form_class(request.POST, request.FILES, instance=post)
        if form.is_valid():
            posts = form.save(commit=False)
            posts.owner = Profile.objects.get(user=request.user)
            if 'post_picture' in request.FILES:
                posts.post_picture = request.FILES['post_picture']
                posts.save()
                messages.success(request, 'Post updated successfully')
                return redirect(self.success_url)
            else:
                messages.error(request, 'Failed to update post')
                return render(request, self.template_name, {'form': form}) and redirect(self.success_url)
        else:
            messages.error(request, 'Failed to update post')
            return render(request, self.template_name, {'form': form})


class DeletePostView(CustomView):
    """
    View for deleting a post.
    """
    template_name = 'post/delete_post.html'
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('show_post')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.post_instance = get_object_or_404(Post, pk=self.kwargs['pk'])  # noqa

    def get(self, request, pk):  # noqa
        post = self.post_instance
        return render(request, self.template_name, {'post': post})

    def post(self, request, pk):  # noqa
        post = self.post_instance
        if post:
            Post.objects.filter(pk=post.pk).delete()

            messages.success(request, 'Post deleted successfully!')
            return redirect(self.success_url)
        else:
            messages.error(request, 'Post not found!')
            return redirect(self.success_url)
