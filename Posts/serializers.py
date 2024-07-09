"""
This module contains serializer for passing data into json format.
"""
from rest_framework import serializers
from .models import Post, PostImageVideo, Like, Comment, Friendship

class PostImageVideoSerializer(serializers.ModelSerializer):
    file = serializers.FileField(max_length=None, use_url=True)
    
    class Meta:
        model = PostImageVideo
        fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

class IsLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    post_images_videos = PostImageVideoSerializer(source="postimagevideos",read_only=True,many=True)
    total_likes = serializers.SerializerMethodField()
    all_likes = IsLikeSerializer(source = "likes",read_only=True,many=True)
    class Meta:
        model = Post
        fields = ('id', 'user', 'content', 'comments', 'post_images_videos', 'all_likes','total_likes')
    
    def get_total_likes(self, obj):
        return Like.objects.filter(post=obj).count()



class FriendshipRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ("from_user", "to_user", "is_accepted")
