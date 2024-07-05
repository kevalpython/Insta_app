"""
This module contains serializer for passing data into json format.
"""

from rest_framework import serializers
from .models import (
    Post,PostImageVideo,Like,Comment,Friendship
)

class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            "user",
            "content",
        )

    def create(self, validated_data):
        post = Post.objects.create(
            user=validated_data["user"],
            content=validated_data["content"],
        )
        return post


class ImageVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostImageVideo
        fields = ("user", "post", "file")

class IsLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ("is_like",)


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ("user", "post", "content")

class FriendshipRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ("from_user", "to_user", "is_accepted")
