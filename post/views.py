from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.urls import reverse_lazy
from account.models import User, Profile
from core.mixin import HttpsOptionNotLogoutMixin as MustBeLogingCustomView
from post.forms import UpdatePostForm, CreatCommentForm
from post.models import Post
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect


class HomePostView(MustBeLogingCustomView):
    """
    The HomePostView class handles both GET and POST requests for displaying and creating comments on posts.
    - The setup method initializes view attributes including the template name,form class,next page URL,user,and posts.
    - The get method renders the template to display posts along with the comment creation form.
    - The post method processes form submissions for creating comments on posts.
      - If the form is valid, it saves the comment and displays a success message.
      - If the form is invalid, it renders the template again with the form and any validation errors.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """Initialize the template_posts, form_class, next_page_show_post, user, posts."""
        self.template_posts = 'post/posts.html'  # noqa
        self.form_class = CreatCommentForm  # noqa
        self.next_page_show_post = reverse_lazy('show_post', kwargs={'pk': kwargs['pk']})  # noqa
        self.user = request.user  # noqa
        self.posts = Post.objects.filter(owner=self.user.profile, is_deleted=False).annotate(  # noqa
            num_likes=Count('likes'),
            num_dislikes=Count('dislikes')
        )
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Handle GET requests.
        Render the template to display posts."""
        return render(request, self.template_posts, {'posts': self.posts, 'form': self.form_class()})

    def post(self, request, *args, **kwargs):
        """Handle POST requests.
        Process form submission for creating a comment."""
        form = self.form_class(request.POST)
        if form.is_valid():
            post_instance = get_object_or_404(Post, pk=kwargs['pk'], owner=self.user.profile)
            comment = form.save(commit=False)
            comment.owner = request.user.profile
            comment.post = post_instance
            comment.save()
            messages.success(request, "You have created a new comment")
            return redirect(self.next_page_show_post)
        return render(request, self.template_posts, {'posts': self.posts, 'form': form})


class Explorer(MustBeLogingCustomView):
    """
    The Explorer class handles both GET and POST requests for exploring posts and adding comments.
    - The setup method initializes view attributes including the template name,form class,next page URL,user,and posts.
    - Get method retrieves posts from all active users, along with their profiles,and renders them on the explorer page.
    - The post method processes form submissions for adding comments to posts.
      - If the form is valid, it saves the comment and displays a success message.
      - If the form is invalid, it renders the explorer page again with the form and any validation errors.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """Initialize the template_explorer, form_class, next_page_show_post, user, posts."""
        self.template_explorer = 'explorer/explorer.html'  # noqa
        self.form_class = CreatCommentForm  # noqa
        self.next_page_explorer = reverse_lazy('explorer', kwargs={'pk': kwargs['pk']})  # noqa
        self.next_page_home = reverse_lazy('home')  # noqa
        # self.next_page_create_profile = reverse_lazy('create_profile')  # noqa
        self.user = request.user  # noqa
        try:
            self.user_profile = self.user.profile
        except ObjectDoesNotExist:
            self.user_profile = None  # noqa
            messages.error(request, "You must have a profile. Please create a profile")
        self.posts = Post.objects.filter(owner=self.user_profile)  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        users_with_profiles = User.objects.filter(is_active=True).prefetch_related('profile')
        user_posts = []
        for self.user in users_with_profiles:
            if hasattr(self.user, 'profile'):
                user_posts.append({
                    'user': self.user,
                    'posts': Post.objects.filter(owner=self.user.profile, is_deleted=False).annotate(
                        num_likes=Count('likes'),
                        num_dislikes=Count('dislikes')
                    )
                })
        return render(request, self.template_explorer,
                      {'posts': self.posts, 'user_posts': user_posts, 'form': self.form_class()})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            post_instance = get_object_or_404(Post, pk=kwargs['pk'])
            comment = form.save(commit=False)
            comment.owner = self.user.profile
            comment.post = post_instance
            comment.save()
            messages.success(request, "You have created a new comment")
            return redirect(self.next_page_explorer)

        return render(request, self.template_explorer, {'form': form})


class CreatePostView(MustBeLogingCustomView):
    """
    The CreatePostView class handles both GET and POST requests for creating a post.
    - The setup method initializes the view attributes including the form class, template name, next page URL, files,
        and user.
    - The get method renders the form for creating a post.
    - The post method processes the form submission for creating a post.
      - If the form is valid, it creates a new post instance, assigns the owner, saves the post, displays a success
            message, and redirects to the page for creating a new post.
      - If the form is invalid, it displays an error message and renders the form again with the error messages.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """Initialize the form_class, template_create_post, next_page_home, files, user."""
        self.form_class = UpdatePostForm  # noqa
        self.template_create_post = 'post/create_post.html'  # noqa
        self.next_page_create_post = reverse_lazy('create_post')  # noqa
        self.files = request.FILES  # noqa
        self.user = request.user  # noqa
        try:
            self.user_profile = Profile.objects.get(user=self.user)
        except ObjectDoesNotExist:
            messages.error(request, "You must have a profile. Please create a profile")
            self.user_profile = None  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        """Render the form for creating a post."""
        return render(request, self.template_create_post, {'form': self.form_class()})

    def post(self, request):
        """Process the form submission for creating a post."""
        form = self.form_class(request.POST, self.files)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = Profile.objects.get(user=self.user)
            if 'post_picture' in self.files:
                post.post_picture = self.files['post_picture']
                post.save()
                messages.success(request, 'Post created successfully!')
                return redirect(self.next_page_create_post)
            else:
                post.save()
                messages.success(request, 'Post created successfully!')
                return render(request, self.template_create_post, {'form': form})
        elif not form.is_valid():
            messages.error(request, 'Failed to create post')
            return redirect(self.template_create_post)
        else:
            return render(request, self.template_create_post, {'form': form})


class FollowUserView(MustBeLogingCustomView):
    template_name = 'explorer/explorer.html'
    success_url = reverse_lazy('explorer')
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        return redirect(self.success_url)

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        profile = Profile.objects.get(pk=user_id)
        current_user_profile = request.user.profile

        current_user_profile.following = profile.user
        current_user_profile.save()

        messages.success(request, f"You are now following {profile.full_name}")

        return redirect(self.success_url)


class UnfollowUserView(MustBeLogingCustomView):
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


class PostLikeView(MustBeLogingCustomView):
    """
    The PostLikeView class handles GET requests for liking/disliking a post.
    - The setup method initializes the view attributes including the next page URL, user, and post instance.
    - The get method processes liking/disliking of a post.
      - If the post is not already liked by the user, it sets the like for the user and removes any existing dislike.
      - If the post is not already disliked by the user, it sets the dislike for the user and removes any existing like.
      - Redirects the user to the next page after processing the request.
    """
    http_method_names = ['get']

    def setup(self, request, *args, **kwargs):
        """Initialize the next_page_explorer_post_id, user, self.post."""
        self.next_page_explorer_post_id = reverse_lazy('explorer', kwargs={'pk': kwargs['post_id']})  # noqa
        self.user = request.user.profile  # noqa
        self.post = get_object_or_404(Post, pk=kwargs['post_id'])  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Handle GET requests.
        Process liking/disliking of a post."""

        if not self.post.likes == self.user:
            """ If the post is not already liked by the user, like the post."""
            self.post.likes = self.user
            self.post.save()
            messages.success(request, "You have liked this post")
            if self.post.dislikes == self.user:
                """If the post was previously disliked by the user, remove the dislike."""
                self.post.dislikes = None
                self.post.save()
                messages.success(request, "You have removed your dislike from this post")
            return redirect(self.next_page_explorer_post_id)

        if not self.post.dislikes == self.user:
            """If the post is not already disliked by the user, dislike the post."""
            self.post.dislikes = self.user  # noqa
            self.post.save()
            messages.success(request, "You have disliked this post")
            if self.post.likes == self.user:
                """If the post was previously liked by the user, remove the like."""
                self.post.likes = None
                self.post.save()
                messages.success(request, "You have removed your like from this post")
        return redirect(self.next_page_explorer_post_id)


class UpdatePostView(MustBeLogingCustomView):
    """
    View for updating a post.
    The UpdatePostView class handles both GET and POST requests for updating a post.
    - The setup method initializes the view attributes including the template name, form class, files, user,
        next page URL, and retrieves the post instance.
    - The get method renders the form for updating a post with the existing post data filled in.
    - The post method processes the form submission for updating a post.
    - If the form is valid, it updates the post with the new data, saves it, and redirects to the page displaying
        the updated post.
    - If the form is invalid, it displays an error message and renders the form again with the error messages.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        self.template_update_post = 'post/update_post.html'  # noqa
        self.form_class = UpdatePostForm  # noqa
        self.files = request.FILES  # noqa
        self.user = request.user  # noqa
        self.next_page_show_post = reverse_lazy('show_post', kwargs={'pk': kwargs['pk']})  # noqa
        self.post_instance = get_object_or_404(Post, pk=kwargs['pk'])  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):  # noqa
        """
        Renders the form for updating a post.
        """
        form = self.form_class(instance=self.post_instance)
        return render(request, self.template_update_post, {'form': form, 'post': self.post_instance})

    def post(self, request, *args, **kwargs):  # noqa
        """
        Processes the form submission for updating a post.
        """
        form = self.form_class(request.POST, self.files, instance=self.post_instance)
        if form.is_valid():
            posts = form.save(commit=False)
            posts.owner = Profile.objects.get(user=self.user)
            if 'post_picture' in self.files:
                posts.post_picture = self.files['post_picture']
                posts.save()
                messages.success(request, 'Post updated successfully')
                return redirect(self.next_page_show_post)
            else:
                messages.error(request, 'Failed to update post')
                return render(request, self.template_update_post, {'form': form}) and redirect(
                    self.template_update_post)
        else:
            messages.error(request, 'Failed to update post')
            return render(request, self.template_update_post, {'form': form})


class DeletePostView(MustBeLogingCustomView):
    """
    View for deleting a post.

    The DeletePostView class handles both GET and POST requests for deleting a post.
    - The setup method initializes the view attributes including the template name, next page URL, and retrieves
         the post instance.
    - The get method renders the delete confirmation page.
    - The post method deletes the post instance, displays a success message, and redirects the user to the page
        displaying the posts.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        self.template_delete_post = 'post/delete_post.html'  # noqa
        self.next_page_show_post = reverse_lazy('show_post', kwargs={'pk': kwargs['pk']})  # noqa
        self.post_instance = get_object_or_404(Post, pk=kwargs['pk'])  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Handle GET request to display delete confirmation page."""
        return render(request, self.template_delete_post, {'post': self.post_instance})

    def post(self, request, *args, **kwargs):
        """Handle POST request to delete the post."""
        if self.post_instance:
            Post.objects.filter(pk=self.post_instance.pk).delete()
            messages.success(request, 'Post deleted successfully!')
            return redirect(self.next_page_show_post)
        else:
            messages.error(request, 'Post not found!')
            return redirect(self.next_page_show_post)
