"""
Serializers for converting Django model instances to JSON format.
"""

from rest_framework import serializers
from Users.models import User
from .models import Post, PostImageVideo, Like, Comment, Friendship
from urllib.parse import urljoin

class PostImageVideoSerializer(serializers.ModelSerializer):
    """
    Serializer for handling PostImageVideo model instances.

    Attributes:
        file (FileField): Field for uploading image or video files.
    """
    
    file = serializers.FileField(max_length=None, use_url=True)
    
    class Meta:
        model = PostImageVideo
        fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for handling Comment model instances.
    """
    
    class Meta:
        model = Comment
        fields = "__all__"
    
class ShowCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for handling Comment model instances.
    """
    username = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ('post', 'content', 'username')
    
    def get_username(self, obj):
        obj.user.username
        return obj.user.username

class IsLikeSerializer(serializers.ModelSerializer):
    """
    Serializer for handling Like model instances.
    """
    
    class Meta:
        model = Like
        fields = "__all__"

class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for handling Post model instances including related comments, images/videos, and likes.

    """
    
    comments = ShowCommentSerializer(many=True, read_only=True)
    post_images_videos = PostImageVideoSerializer(source="postimagevideos", read_only=True, many=True)
    user_name = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    has_like = serializers.SerializerMethodField()
    all_likes = IsLikeSerializer(source="likes", read_only=True, many=True)

    class Meta:
        model = Post
        fields = ('id', 'user_name', 'content', 'comments', 'post_images_videos', 'has_like', 'all_likes', 'total_likes')
    
    def get_total_likes(self, obj):
        """
        Method to get the total number of likes on a post.

        Args:
            obj (Post): The Post instance.

        Returns:
            int: The total number of likes on the post.
        """
        return Like.objects.filter(post=obj, is_like=True).count()

    def get_user_name(self, obj):
        """
        Method to get the username of the post owner.

        Args:
            obj (Post): The Post instance.

        Returns:
            str: The username of the post owner.
        """
        return obj.user.username
    
    def get_has_like(self, obj):
        """
        Method to check if the authenticated user has liked the post.

        Args:
            obj (Post): The Post instance.

        Returns:
            bool or None: True if the authenticated user has liked the post, False otherwise. None if not authenticated.
        """
        like = Like.objects.filter(user=self.context['user'], post=obj).first()
        if like:
            return like.is_like
        return None

class AddPostSerializer(serializers.ModelSerializer):
    """
    Serializer for adding a new Post instance.

    This serializer is used to create a new Post instance through API requests.

    Attributes:
        Meta (class): Meta class specifying the model and fields to include.
    """
    
    class Meta:
        model = Post
        fields = ('user', 'content')
    
class FriendshipRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for handling Friendship model instances, specifically for friendship requests.

    Attributes:
        from_user (SerializerMethodField): Method field to retrieve the username of the user sending the request.
        to_user (SerializerMethodField): Method field to retrieve the username of the user receiving the request.
        from_user_img (SerializerMethodField): Method field to retrieve the profile image URL of the user sending the request.
    """
    
    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    from_user_img = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ("id", "from_user", "to_user", "is_accepted", "from_user_img")
        
    def get_from_user(self, obj):
        """
        Method to get the username of the user sending the friendship request.

        Args:
            obj (Friendship): The Friendship instance.

        Returns:
            str: The username of the user sending the request.
        """
        return obj.from_user.username
    
    def get_to_user(self, obj):
        """
        Method to get the username of the user receiving the friendship request.

        Args:
            obj (Friendship): The Friendship instance.

        Returns:
            str: The username of the user receiving the request.
        """
        return obj.to_user.username
    
    def get_from_user_img(self, obj):
        """
        Method to get the profile image URL of the user sending the friendship request.

        Args:
            obj (Friendship): The Friendship instance.

        Returns:
            str or None: The profile image URL of the user sending the request if available, otherwise None.
        """
        request = self.context.get('request')
        profile_image = obj.from_user.profile_img
        if profile_image and request:
            return urljoin(request.build_absolute_uri('/'), profile_image.url)
        return None

class UsernameSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving usernames from User model instances.

    Attributes:
        Meta (class): Meta class specifying the model and fields to include.
    """
    profile_img = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ("username","profile_img")

    def get_profile_img(self, obj):
        """
        Method to get the profile image URL of the user sending the friendship request.

        Args:
            obj (Friendship): The Friendship instance.

        Returns:
            str or None: The profile image URL of the user sending the request if available, otherwise None.
        """
        request = self.context.get('request')
        profile_image = obj.profile_img
        print("======>>>>>>>",obj.profile_img)
        if profile_image and request:
            return urljoin(request.build_absolute_uri('/'), profile_image.url)
        return None
    