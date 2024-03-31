from django.contrib import admin
from .models import Post, Comment, Vote, Image, CommentLike


class CommentInline(admin.TabularInline):
    """
    Defines an inline admin option for the Comment model, which allows comments to be displayed inline within
        the admin interface when viewing posts.
    Specifies the model to be used for the inline comments, sets whether comments can be deleted inline, and
        provides options for customizing the display, such as the verbose name for plural comments and the foreign
        key name linking comments to posts.
    """
    model = Comment
    can_delete = False
    verbose_name_plural = 'Comment'
    fk_name = 'post'


class VoteInline(admin.TabularInline):
    """
    Defines an inline admin option for the Vote model, allowing votes to be displayed inline within the admin
        interface when viewing posts.
    Specifies the model for the inline votes, sets whether votes can be deleted inline, and provides options
        for customizing the display, such as the verbose name for plural votes and the foreign key name linking
        votes to posts.
    """
    model = Vote
    verbose_name_plural = 'Vote'
    fk_name = 'post'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """
    Registers the Vote model with the admin interface.
    Specifies the display options for the Vote model in the admin interface, including the fields to be displayed in
        the list view, filters, search fields, ordering, and row ID fields.
    """
    list_display = ('user', 'post', 'create_time')
    list_filter = ('user', 'post')
    search_fields = ['user', 'post']
    ordering = ('-create_time',)
    row_id_fields = ('user', 'post',)


class CommentLikeInline(admin.TabularInline):
    model = CommentLike
    verbose_name_plural = 'CommentLike'
    fk_name = 'comment'
    ordering = ('-create_time',)
    row_id_fields = ('user', 'comment',)


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'create_time')
    list_filter = ('user', 'comment')
    search_fields = ['user', 'comment']
    ordering = ('-create_time',)
    row_id_fields = ('user', 'comment',)


class ImageInline(admin.TabularInline):
    model = Image
    can_delete = False
    fk_name = 'post_image'
    ordering = ('-create_time',)
    row_id_fields = ('post_image',)
    list_display = ('post_image', 'images', 'is_active', 'create_time', 'update_time')
    list_filter = ('post_image', 'is_deleted',)
    search_fields = ('post_image__username', 'create_time', 'update_time')


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('post_image', 'images', 'is_active', 'create_time', 'update_time')
    list_filter = ('is_active',)
    search_fields = ('post_image__username', 'create_time', 'update_time')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Registers the Post model with the admin interface.
    Specifies the display options for the Post model in the admin interface, including the fields to be displayed
     in the list view, filters, search fields, ordering, and row ID fields.
    Includes inline options for displaying comments and votes related to each post.
    """
    list_display = ('owner', 'title', 'update_time')
    list_filter = ('owner', 'title')
    search_fields = ['owner', 'update_time']
    ordering = ('-update_time',)
    row_id_fields = ('owner',)
    inlines = (CommentInline, VoteInline, ImageInline)

    def get_inline_instances(self, request, obj=None):
        """
        Overrides the get_inline_instances method to conditionally display inline instances based on whether an
            object is being edited.
        If no object is provided, returns an empty list to prevent inline instances from being displayed.
        Otherwise, calls the parent class's get_inline_instances method to retrieve inline instances.
        """
        if not obj:
            return list()
        return super(PostAdmin, self).get_inline_instances(request, obj)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Registers the Comment model with the admin interface.
    Specifies the display options for the Comment model in the admin interface, including the fields to be
        displayed in the list view, filters, search fields, ordering, and row ID fields.
    """
    list_display = ('owner', 'post', 'create_time', 'is_reply')
    list_filter = ('owner', 'post')
    search_fields = ['owner', 'post']
    ordering = ('-update_time', '-create_time')
    row_id_fields = ('owner', 'post', 'reply')
    inlines = (CommentLikeInline,)

    def get_inline_instances(self, request, obj=None):
        """
        Overrides the get_inline_instances method to conditionally display inline instances based on whether an
            object is being edited.
        If no object is provided, returns an empty list to prevent inline instances from being displayed.
        Otherwise, calls the parent class's get_inline_instances method to retrieve inline instances.
        """
        if not obj:
            return list()
        return super(CommentAdmin, self).get_inline_instances(request, obj)
