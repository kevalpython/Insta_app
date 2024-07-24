"""
Views for handling API endpoints related to posts, comments, likes, friendships, and user interactions.
"""

import json
import os
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .management.authentication import JWTAuthentication
from .models import *
from .serializers import (
    AddPostSerializer,
    CommentSerializer,
    FriendshipRequestSerializer,
    PostImageVideoSerializer,
    PostSerializer,
    UsernameSerializer,
    FriendsListSerializer,
)


class UserPostView(viewsets.ViewSet):
    """
    ViewSet for retrieving posts of a specific user or listing all posts of the authenticated user.
    """

    authentication_classes = [JWTAuthentication]

    def create(self, request):
        """
        Handles POST request to create a new post with optional images/videos.

        Returns:
            Response: JSON response indicating success or failure of post creation.
        """
        user = request.user.id
        files = request.FILES.getlist("files")
        data = {"user": user, "content": request.data["content"]}
        add_post_serializer = AddPostSerializer(data=data)
        if add_post_serializer.is_valid():
            post = add_post_serializer.save()
            if files:
                for file in files:
                    file_extension = os.path.splitext(file.name)[1].lower()
                    if file_extension in [".mp4", ".mov", ".avi"]:
                        file_type = "video"
                    else:
                        file_type = "image"

                    image_data = {
                        "user": user,
                        "file": file,
                        "post": post.id,
                        "file_type": file_type,
                    }
                    image_serializer = PostImageVideoSerializer(data=image_data)
                    if image_serializer.is_valid():
                        image_serializer.save()
            return Response({"msg": "Post Created"}, status=status.HTTP_201_CREATED)
        return Response(add_post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """
        Handles GET request to list posts of the authenticated user and their friends.

        Returns:
            Response: JSON response with list of posts and associated data.
        """
        context = {"request": request, "user": request.user}
        user = request.user

        friends_ids = Friendship.objects.filter(
            Q(from_user=user, is_accepted=True)
            | Q(to_user=user, is_follow_back_accepted=True)
        ).values_list("from_user", "to_user")

        friends_ids = set(
            friend_id
            for friend_pair in friends_ids
            for friend_id in friend_pair
            if friend_id != user.id
        )

        posts = Post.objects.filter(
            Q(user=user) | Q(user__id__in=friends_ids)
        ).order_by("-created_at")

        post_serializer = PostSerializer(posts, context=context, many=True)
        return Response(post_serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        Handles GET request to retrieve posts of a specific user.

        Returns:
            Response: JSON response with list of posts and associated data of the specified user.
        """
        context = {"request": request, "user": request.user}
        user = User.objects.get(pk=pk)
        queryset = Post.objects.filter(user=user).order_by("-created_at")
        total_post = queryset.count()
        total_friends = Friendship.objects.filter(
            Q(from_user=user, is_accepted=True)
            | Q(to_user=user, is_follow_back_accepted=True)
        ).count()
        user_serializer = UsernameSerializer(user, context=context)
        post_serializer = PostSerializer(queryset, context=context, many=True)
        return Response(
            {
                "posts": post_serializer.data,
                "total_posts": total_post,
                "total_friends": total_friends,
                "username": user_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, pk=None):
        """
        Handles DELETE request to delete a post.

        Returns:
            Response: JSON response indicating success or failure of post deletion.
        """
        post = Post.objects.filter(pk=pk, user=request.user.id)
        if post:
            post.delete()
            return Response({"msg": "Post Deleted"}, status=status.HTTP_201_CREATED)
        return Response({"msg": "Post Not Found"}, status=status.HTTP_404_NOT_FOUND)


class LikePostView(viewsets.ViewSet):
    """
    ViewSet for liking/unliking a post.
    """

    authentication_classes = [JWTAuthentication]

    def retrieve(self, request, pk=None):
        """
        Handles GET request to like/unlike a post.

        Returns:
            Response: JSON response indicating success or failure of like/unlike operation.
        """
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                {"msg": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        like, created = Like.objects.get_or_create(post=post, user=request.user)

        if created or not like.is_like:
            like.is_like = True
            like.save()
            return Response(
                {"msg": "Liked Post"},
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        else:
            like.is_like = False
            like.save()
            return Response({"msg": "Unliked Post"}, status=status.HTTP_200_OK)


class AddCommentView(viewsets.ViewSet):
    """
    ViewSet for adding comments to a post.
    """

    authentication_classes = [JWTAuthentication]

    def create(self, request):
        """
        Handles POST request to add a comment to a post.

        Returns:
            Response: JSON response indicating success or failure of comment creation.
        """
        data = {
            "post": request.data["post_id"],
            "user": request.user.id,
            "content": request.data["comment"],
        }
        add_post_serializer = CommentSerializer(data=data)
        if add_post_serializer.is_valid():
            add_post_serializer.save()
            return Response({"msg": "Comment Created"}, status=status.HTTP_201_CREATED)
        return Response(add_post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FriendshipView(viewsets.ViewSet):
    """
    ViewSet for sending and handling friend requests, follow-back requests, and managing friend lists.

    """

    authentication_classes = [JWTAuthentication]

    @action(detail=True, methods=["post"])
    def send_request(self, request, pk=None):
        """
        Send a friend request to another user.

        Returns:
            Response: A response indicating whether the friend request was sent successfully or if it already exists.
        """
        try:
            to_user = get_object_or_404(User, pk=pk)
            friend_request, created = Friendship.objects.get_or_create(
                from_user=request.user, to_user=to_user
            )
            if created:
                return Response(
                    {"msg": "Friend request sent"}, status=status.HTTP_201_CREATED
                )
            return Response(
                {"msg": "Friend request already sent"}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"msg": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["post"])
    def send_follow_back_request(self, request, pk=None):
        """
        Send a follow-back request to a user who has already sent a friend request and it has been accepted.

        Returns:
            Response: A response indicating whether the follow-back request was sent successfully.
        """
        try:
            to_user = get_object_or_404(User, pk=pk)
            follow_back_request = Friendship.objects.filter(
                is_follow_back_requested=False,
                to_user=request.user,
                from_user=to_user,
                is_accepted=True,
            ).first()
            if follow_back_request:
                follow_back_request.is_follow_back_requested = True
                follow_back_request.save()
                return Response(
                    {"msg": "Follow back request sent"}, status=status.HTTP_201_CREATED
                )
        except User.DoesNotExist:
            return Response(
                {"msg": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["post"])
    def handle_request(self, request, pk=None):
        """
        Handle a friend or follow-back request by accepting, rejecting, or unfollowing.

        Returns:
            Response: A response indicating the outcome of the request handling.
        """
        action = request.data.get("action")
        try:
            friendrequest = Friendship.objects.filter(
                Q(from_user=pk, to_user=request.user, is_accepted=False)
                | Q(from_user=request.user, to_user=pk, is_accepted=True)
                | Q(to_user=request.user, from_user=pk, is_follow_back_accepted=True)
            ).first()
            if action == "accept":
                if (
                    friendrequest.from_user == request.user
                    and friendrequest.is_follow_back_requested
                    and not friendrequest.is_follow_back_accepted
                ):
                    friendrequest.is_follow_back_accepted = True
                else:
                    friendrequest.is_accepted = True
                friendrequest.save()
                return Response(
                    {"msg": "Request accepted"}, status=status.HTTP_201_CREATED
                )
            elif action == "reject":
                if friendrequest.to_user == request.user:
                    friendrequest.delete()
                return Response(
                    {"msg": "Request rejected"}, status=status.HTTP_201_CREATED
                )
            elif action == "unfollow":
                if (
                    friendrequest.is_accepted
                    and friendrequest.from_user == request.user
                ):
                    friendrequest.delete()
                elif (
                    friendrequest.to_user == request.user
                    and friendrequest.is_follow_back_accepted
                ):
                    friendrequest.is_follow_back_accepted = False
                    friendrequest.is_follow_back_requested = False
                    friendrequest.save()
                return Response(
                    {"msg": "Unfollowed successfully"}, status=status.HTTP_200_OK
                )
        except User.DoesNotExist:
            return Response(
                {"msg": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"], url_path="list_requests")
    def list_requests(self, request):
        """
        List all pending friend requests and follow-back requests for user.

        Returns:
            Response: A response containing a list of pending requests.
        """
        context = {"request": request}
        friend_request = Friendship.objects.filter(
            Q(to_user=request.user, is_accepted=False)
            | Q(
                from_user=request.user,
                is_follow_back_requested=True,
                is_follow_back_accepted=False,
            )
        )
        friend_request_serializer = FriendshipRequestSerializer(
            friend_request, context=context, many=True
        )
        return Response(friend_request_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="list_friends")
    def list_friends(self, request):
        """
        List all friends of user.

        Returns:
            Response: A response containing a list of friends.
        """
        context = {"request": request}
        friend_request = Friendship.objects.filter(
            Q(from_user=request.user, is_accepted=True)
            | Q(to_user=request.user, is_accepted=True)
        )
        friend_request_serializer = FriendsListSerializer(
            friend_request, context=context, many=True
        )
        return Response(friend_request_serializer.data, status=status.HTTP_200_OK)
