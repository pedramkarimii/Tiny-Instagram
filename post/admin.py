from django.contrib import admin
from .models import Post, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    # add_form = CommentForm
    can_delete = False
    verbose_name_plural = 'Comment'
    fk_name = 'post'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('owner', 'title', 'update_time')
    list_filter = ('owner', 'title')
    search_fields = ['owner', 'update_time']
    ordering = ('-update_time',)
    row_id_fields = ('owner',)
    inlines = (CommentInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(PostAdmin, self).get_inline_instances(request, obj)


@admin.register(Comment)
class CommentInline(admin.ModelAdmin):
    list_display = ('owner', 'post', 'create_time', 'reply')
    list_filter = ('owner', 'post')
    search_fields = ['owner', 'post']
    ordering = ('-update_time', '-create_time')
    row_id_fields = ('owner', 'post',  'reply')
