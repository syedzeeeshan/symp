from django.contrib import admin
from .models import User, Post

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'is_published', 'created_at']
    search_fields = ['title', 'content']
    list_filter = ['is_published', 'created_at', 'author']
    readonly_fields = ['created_at', 'updated_at']
