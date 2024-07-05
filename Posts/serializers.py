"""
This module contains serializer for passing data into json format.
"""
from rest_framework import serializers
from .models import Post, PostImageVideo, Like, Comment, Friendship

class PostImageVideoSerializer(serializers.ModelSerializer):
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
    likes_count = serializers.SerializerMethodField()
    images_videos = PostImageVideoSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ('id', 'user', 'content', 'comments', 'likes_count', 'images_videos')

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def create(self, validated_data):
        images_videos_data = validated_data.pop('images_videos', [])
        post = Post.objects.create(**validated_data)

        for image_video_data in images_videos_data:
            PostImageVideo.objects.create(post=post, **image_video_data)

        return post


class FriendshipRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ("from_user", "to_user", "is_accepted")
