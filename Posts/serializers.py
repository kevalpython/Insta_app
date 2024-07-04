"""
This module contains serializer for passing data into json format.
"""

from rest_framework import serializers
from .models import (
    Post,PostImageVideo
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

