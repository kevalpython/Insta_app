"""
Serializers for converting Django model instances to JSON format.
"""

from rest_framework import serializers
from Users.models import User
from .models import Post, PostImageVideo, Like, Comment, Friendship
from urllib.parse import urljoin
from django.db.models import Q


class PostImageVideoSerializer(serializers.ModelSerializer):
    """
    Serializer for handling PostImageVideo model instances.
    """

    file = serializers.FileField(max_length=None, use_url=True)

    class Meta:
        model = PostImageVideo
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for handling Comment model instances.
    """

    username = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("post", "user", "content", "username")

    def get_username(self, obj):
        return obj.user.username


class LikeSerializer(serializers.ModelSerializer):
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

    comments = CommentSerializer(many=True, read_only=True)
    post_images_videos = PostImageVideoSerializer(
        source="postimagevideos", read_only=True, many=True
    )
    user_name = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    has_like = serializers.SerializerMethodField()
    all_likes = LikeSerializer(source="likes", read_only=True, many=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "user_name",
            "content",
            "comments",
            "post_images_videos",
            "has_like",
            "all_likes",
            "total_likes",
        )

    def get_total_likes(self, obj):
        """
        Method to get the total number of likes on a post.

        Returns:
            int: The total number of likes on the post.
        """
        return Like.objects.filter(post=obj, is_like=True).count()

    def get_user_name(self, obj):
        """
        Method to get the username of the post owner.

        Returns:
            str: The username of the post owner.
        """
        return obj.user.username

    def get_has_like(self, obj):
        """
        Method to check if the authenticated user has liked the post.

        Returns:
            bool or None: True if the authenticated user has liked the post, False otherwise. None if not authenticated.
        """
        like = Like.objects.filter(user=self.context["user"], post=obj).first()
        if like:
            return like.is_like
        return None


class AddPostSerializer(serializers.ModelSerializer):
    """
    Serializer for adding a new Post instance.
    """

    class Meta:
        model = Post
        fields = ("user", "content")


class FriendshipRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for handling Friendship model instances, specifically for friendship requests.
    """

    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    user_img = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ("id", "from_user", "to_user", "user_img", "user_id")

    def get_from_user(self, obj):
        """
        Method to get the username of the user sending the friendship request.

        Returns:
            str: The username of the user sending the request.
        """
        return obj.from_user.username

    def get_to_user(self, obj):
        """
        Method to get the username of the user receiving the friendship request.

        Returns:
            str: The username of the user receiving the request.
        """
        return obj.to_user.username

    def get_user_img(self, obj):
        """
        Method to get the profile image URL of the user sending the friendship request.

        Returns:
            str or None: The profile image URL of the user sending the request if available, otherwise None.
        """
        request = self.context.get("request")
        if obj.from_user == request.user:
            profile_image = obj.to_user.profile_img
        else:
            profile_image = obj.from_user.profile_img
        if profile_image and request:
            return urljoin(request.build_absolute_uri("/"), profile_image.url)
        return None

    def get_user_id(self, obj):
        """
        Method to get the profile image URL of the user sending the friendship request.

        Returns:
            str or None: The profile image URL of the user sending the request if available, otherwise None.
        """
        request = self.context.get("request")
        if obj.from_user == request.user:
            return obj.to_user.id
        else:
            return obj.from_user.id


class UsernameSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving usernames from User model instances.
    """

    profile_img = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("username", "profile_img")

    def get_profile_img(self, obj):
        """
        Method to get the profile image URL of the user sending the friendship request.

        Returns:
            str or None: The profile image URL of the user sending the request if available, otherwise None.
        """
        request = self.context.get("request")
        profile_image = obj.profile_img
        if profile_image and request:
            return urljoin(request.build_absolute_uri("/"), profile_image.url)
        return None


class FriendsListSerializer(serializers.ModelSerializer):
    """
    Serializer for handling Friendship model instances, specifically for friendship requests.
    """

    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()
    user_img = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    friend_request = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = (
            "id",
            "from_user",
            "to_user",
            "user_img",
            "user_id",
            "friend_request",
        )

    def get_from_user(self, obj):
        """
        Method to get the username of the user sending the friendship request.

        Returns:
            str: The username of the user sending the request.
        """
        return obj.from_user.username

    def get_to_user(self, obj):
        """
        Method to get the username of the user receiving the friendship request.

        Returns:
            str: The username of the user receiving the request.
        """
        return obj.to_user.username

    def get_user_img(self, obj):
        """
        Method to get the profile image URL of the user sending the friendship request.

        Returns:
            str or None: The profile image URL of the user sending the request if available, otherwise None.
        """
        request = self.context.get("request")
        if obj.from_user == request.user:
            profile_image = obj.to_user.profile_img
        else:
            profile_image = obj.from_user.profile_img
        if profile_image and request:
            return urljoin(request.build_absolute_uri("/"), profile_image.url)
        return None

    def get_user_id(self, obj):
        """
        Method to get the profile image URL of the user sending the friendship request.

        Returns:
            str or None: The profile image URL of the user sending the request if available, otherwise None.
        """
        request = self.context.get("request")
        if obj.from_user == request.user:
            return obj.to_user.id
        else:
            return obj.from_user.id

    def get_friend_request(self, obj):
        """
        Method to get the friend request status for a user.

        Returns:
            str: Status of friend request ('accepted', 'requested', 'not').
        """
        request = self.context.get("request")
        user = request.user
        if (
            obj.to_user == user
            and obj.is_follow_back_requested == True
            and obj.is_follow_back_accepted == True
        ):
            return "accepted"
        elif (
            obj.to_user == user
            and obj.is_follow_back_requested == True
            and obj.is_follow_back_accepted == False
        ):
            return "follow_back_requested"
        elif obj.to_user == user and obj.is_follow_back_requested == False:
            return "follow_back_request"
        else:
            return "accepted"
