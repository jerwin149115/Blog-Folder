from django.contrib import admin
from .models import Category, Tag, Post, Comment

admin.site.register(Category)
admin.site.register(Tag)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at')
    search_fields = ('title', 'content')
    list_filter = ('category', 'tags', 'author')
    prepopulated_fields = {'slug': ('title',)} 

admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')
    search_fields = ('content',)

admin.site.register(Comment, CommentAdmin)
