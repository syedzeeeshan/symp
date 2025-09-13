from rest_framework import serializers
from .models import User, Post

class UserSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'created_at', 'updated_at', 'posts_count']

    def get_posts_count(self, obj):
        return obj.posts.count()

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'author_name', 
                 'created_at', 'updated_at', 'is_published']
