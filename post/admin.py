from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('owner', 'title', 'update_time')
    list_filter = ("owner", 'title')
    search_fields = ['owner', 'update_time']
    ordering = ('-update_time',)
    row_id_fields = ('owner',)
