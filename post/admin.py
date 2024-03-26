from django.contrib import admin
from .models import Post, Comment, Vote


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
    can_delete = False
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
    inlines = (CommentInline, VoteInline)

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
