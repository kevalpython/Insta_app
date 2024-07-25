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
    user_name = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    has_like = serializers.SerializerMethodField()

    all_likes = IsLikeSerializer(source = "likes",read_only=True,many=True)
    class Meta:
        model = Post
        fields = ('id', 'user_name', 'content', 'comments', 'post_images_videos', 'has_like','all_likes','total_likes')
    
    def get_total_likes(self, obj):
        return Like.objects.filter(post=obj, is_like=True).count()

    def get_user_name(self, obj):
        return obj.user.username
    
    def get_has_like(self,obj):
        like=Like.objects.filter(user=self.context['user'],post=obj).first()
        print(like.is_like)
        return like.is_like


class FriendshipRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ("from_user", "to_user", "is_accepted")
