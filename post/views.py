from django.contrib.postgres.search import TrigramSimilarity
from django.views.generic import DetailView
from post.forms import SearchForm
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from account.models import User, Profile, Relation
from core.mixin import HttpsOptionNotLogoutMixin as MustBeLogingCustomView
from post.forms import UpdatePostForm, CreatCommentForm
from post.models import Post, Vote
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect


class HomePostView(MustBeLogingCustomView):
    """
    View for displaying and creating comments on posts.

    Attributes:
    - template_posts (str): The template for rendering posts.
    - form_class (CreatCommentForm): The form class for creating comments.
    - form_class_search (SearchForm): The form class for searching posts.
    - next_page_show_post (reverse_lazy): The URL pattern for displaying a specific post.
    - user (User): The current user.
    - posts (QuerySet): The queryset of posts filtered by the current user and not deleted.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        print(kwargs)
        """
        Initializes form classes, template, and queryset of posts.
        """
        self.template_posts = 'post/posts.html'  # noqa
        self.form_class = CreatCommentForm  # noqa
        self.form_class_search = SearchForm  # noqa
        self.next_page_show_post = reverse_lazy('show_post', kwargs={'pk': kwargs['pk']})  # noqa
        self.user = request.user  # noqa
        self.posts = Post.objects.filter(owner=self.user.profile, is_deleted=False)  # noqa

        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
       Handles GET requests, including post searching.
       """
        form_search = self.form_class_search(request.GET)
        search_query = request.GET.get('search')
        if search_query:
            self.posts = self.posts.annotate(  # noqa
                similarity=TrigramSimilarity('title', search_query) +
                           TrigramSimilarity('body', search_query)
            ).filter(similarity__gt=0.1).order_by('-similarity')

        return render(request, self.template_posts,
                      {'posts': self.posts, 'form': self.form_class(), 'form_search': form_search})

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests for creating comments.
        """
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
        """Initialize the template_explorer, form_class_search, next_page_home, next_page_explorer, posts."""
        self.template_explorer = 'explorer/explorer.html'  # noqa
        self.form_class_search = SearchForm  # noqa
        self.next_page_home = reverse_lazy('home')  # noqa
        self.posts = Post.objects.filter(owner=request.user.profile)  # noqa
        self.next_page_explorer = reverse_lazy('explorer')  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """This method handles GET requests for the Explorer view.
           It retrieves the search form data and all posts from the database.
           If the search form is valid, it performs a trigram similarity search on the Post model
           based on the title and body fields.
           It then filters the posts based on the search similarity score and orders them by similarity.
           Next, it retrieves all active users with their profiles and prepares a list of user posts.
           Finally,it combines the search results and user posts into a list of tuples and renders the explorer template
           """
        form_search = self.form_class_search(request.GET)
        post_search = Post.objects.all()

        if form_search.is_valid():
            search_query = form_search.cleaned_data.get('search')
            post_search = post_search.annotate(
                similarity=TrigramSimilarity('title', search_query) + TrigramSimilarity('body', search_query)).filter(
                similarity__gt=0.1).order_by('-similarity')
        return render(request, self.template_explorer,
                      {'post_search': post_search,
                       'form_search': form_search})


class PostDetailView(MustBeLogingCustomView, DetailView):
    """
    View for displaying detailed information about a single post.
    """

    http_method_names = ['get', 'post']
    model = Post
    template_name = 'post/post_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        """
        Returns the post object for the detail view.
        """
        return get_object_or_404(Post, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        """
        Adds the comment form to the context data.
        """
        context = super().get_context_data(**kwargs)
        context['form'] = CreatCommentForm()
        return context

    def post(self, request, *args, **kwargs):
        """
        Handles the submission of the comment form.
        """
        post = self.get_object()

        form = CreatCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.owner = request.user.profile
            comment.post = post
            comment.save()
            return redirect(reverse_lazy('post_detail',
                                         kwargs={
                                             'pk': post.pk}))
        else:
            return self.render_to_response(self.get_context_data(form=form))


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
        if not self.user_profile and self.user_profile == None:  # noqa
            return redirect(self.next_page_home)
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
                messages.error(request, 'Failed to create post')
                return redirect(self.template_create_post)
        else:
            return render(request, self.template_create_post, {'form': form})


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
        """Initialize attributes for the template_update_post, form class, files, user,
                   next_page_show_post, next_page_show_update_post and retrieve the post instance."""
        self.template_update_post = 'post/update_post.html'  # noqa
        self.form_class = UpdatePostForm  # noqa
        self.files = request.FILES  # noqa
        self.user = request.user  # noqa
        self.next_page_show_post = reverse_lazy('show_post', kwargs={'pk': kwargs['pk']})  # noqa
        self.next_page_show_update_post = reverse_lazy('update_post', kwargs={'pk': kwargs['pk']})  # noqa
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
                messages.error(request, 'Failed to update post add or change post picture')
                return redirect(self.next_page_show_update_post)
        else:
            messages.error(request, 'Failed to update post')
            return render(request, self.template_update_post, {'form': form})


class FollowUserView(MustBeLogingCustomView):
    """
    A view for allowing users to follow or unfollow another user.
    """
    http_method_names = ['post']

    def setup(self, request, *args, **kwargs):
        """
        Initializes necessary attributes for the view.
        Sets up the user instance to follow/unfollow and defines the next page URL.
        """
        # self.post_instance = get_object_or_404(Post, pk=kwargs['pk'], is_active=True)  # noqa
        self.users_instance = get_object_or_404(User, pk=kwargs['pk'], is_active=True)  # noqa
        self.user = request.user  # noqa
        self.next_page_post_detail = reverse_lazy('post_detail', kwargs={'pk': kwargs['pk']})  # noqa
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request for following or unfollowing a user.

        Checks if a relation already exists between the users. If it exists, unfollows the user;otherwise,creates a new
        relation to follow the user.
        """
        # posts = Post.objects.filter(is_active=True, pk=kwargs['pk']).first()  # noqa
        # if self.post_instance.is_active:  # Check if the user instance is active
        #     # Handle follow/unfollow logic here
        #     # This is just a placeholder, replace it with your actual logic
        #     return redirect(self.next_page_explorer)
        # else:
        #     # User instance is not active, handle accordingly (e.g., show an error message)
        #     # Redirect to an appropriate page
        #     return redirect(self.next_page_explorer)
        relation = Relation.objects.filter(
            followers=self.user,
            following=self.users_instance,
        )
        if relation.exists():
            relation.delete()
            messages.success(request, f"You are unfollow this user {self.users_instance}.")
            return redirect(self.next_page_post_detail)
        elif not relation.exists():
            Relation.objects.create(
                followers=self.user,
                following=self.users_instance,
                is_follow=True
            )
            messages.success(request, f"You are now following {self.users_instance} .")
            return redirect(self.next_page_post_detail)
        else:
            messages.error(request, "Failed to follow user")
            return redirect(self.next_page_post_detail)


class PostLikeView(MustBeLogingCustomView):
    """
    A view for allowing users to like or unlike a post.
    """
    http_method_names = ['get']

    def setup(self, request, *args, **kwargs):
        """
        Initializes necessary attributes for the view.

        Sets up the next page URL, user instance, and the post instance.
        """
        self.next_page_explorer_post_id = reverse_lazy('post_detail', kwargs={'pk': kwargs['post_id']})  # noqa
        self.user = request.user  # noqa
        self.post = get_object_or_404(Post, pk=kwargs['post_id'])  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles the GET request for liking or unliking a post.

        Checks if the user has already liked the post. If not, creates a new like. If yes, removes the like.
        """
        like = Vote.objects.filter(post=self.post, user=self.user)  # noqa
        if not like.exists():
            like.create(post=self.post, user=self.user)
            messages.success(request, f"You have liked this post {self.post.title}")
            return redirect(self.next_page_explorer_post_id)
        else:
            like.delete()
            messages.success(request, f"You have removed your like from this post {self.post.title}")
            return redirect(self.next_page_explorer_post_id)


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
