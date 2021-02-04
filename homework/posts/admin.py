from django.contrib import admin

from .models import Group, Post, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text', )
    list_filter = ('pub_date', )
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('slug', )
    list_filter = ('slug', )
    empty_value_display = '-пусто-'


class CommentsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'author', 'post', 'created')
    search_fields = ('text', )
    list_filter = ('post', )


class FollowsAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_select_related = ('user', )
    list_filter = ('user', )


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentsAdmin)
admin.site.register(Follow, FollowsAdmin)
