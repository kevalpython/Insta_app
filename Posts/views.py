"""
Views for handling API endpoints related to posts, comments, likes, friendships, and user interactions.
"""

from .models import *
import json
from .serializers import (
    PostSerializer,
    CommentSerializer,
    FriendshipRequestSerializer,
    PostImageVideoSerializer,
    AddPostSerializer,
    UsernameSerializer,
)
from rest_framework import status, viewsets
from Users.serializers import UserSerializer
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .management.authentication import JWTAuthentication

class AddPostView(viewsets.ViewSet):
    """
    ViewSet for creating a new post with optional images/videos.

    Attributes:
        authentication_classes (list): List of authentication classes for verifying user authentication.
    """
    
    authentication_classes = [JWTAuthentication]
    
    def create(self, request):
        """
        Handles POST request to create a new post with optional images/videos.

        Args:
            request (Request): HTTP request object containing user data and post content.

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
                    image_data = {"user": user, "file": file, "post": post.id}
                    image_serialzer = PostImageVideoSerializer(data=image_data)
                    if image_serialzer.is_valid():
                        image_serialzer.save()
            return Response({"msg": "Post Created"}, status=status.HTTP_201_CREATED)
        return Response(add_post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostListView(viewsets.ViewSet):
    """
    ViewSet for listing posts of the authenticated user and their friends.

    Attributes:
        authentication_classes (list): List of authentication classes for verifying user authentication.
    """
    
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        """
        Handles GET request to list posts of the authenticated user and their friends.

        Args:
            request (Request): HTTP request object containing user data.

        Returns:
            Response: JSON response with list of posts and associated data.
        """
        context = {"request": request, "user": request.user}
        user = request.user

        friends_ids = Friendship.objects.filter(
            Q(from_user=user, is_accepted=True) | Q(to_user=user, is_accepted=True)
        ).values_list('from_user', 'to_user')

        # Extract the user IDs from the friendships
        friends_ids = set(friend_id for friend_pair in friends_ids for friend_id in friend_pair if friend_id != user.id)

        posts = Post.objects.filter(
            Q(user=user) | Q(user__id__in=friends_ids)
        ).order_by("-created_at")

        post_serializer = PostSerializer(posts, context=context, many=True)
        return Response(post_serializer.data, status=status.HTTP_200_OK)

class PostView(viewsets.ViewSet):
    """
    ViewSet for retrieving posts of a specific user or listing all posts of the authenticated user.

    Attributes:
        authentication_classes (list): List of authentication classes for verifying user authentication.
    """
    
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        """
        Handles GET request to list all posts of the authenticated user.

        Args:
            request (Request): HTTP request object containing user data.

        Returns:
            Response: JSON response with list of posts and associated data.
        """
        context = {"request": request, 'user': request.user}
        user = self.request.user
        queryset = Post.objects.filter(user=user).order_by("-created_at")
        total_post = queryset.count()
        total_friends = Friendship.objects.filter(Q(from_user=user, is_accepted=True) | Q(to_user=user, is_accepted=True)).count()
        user_serializer = UsernameSerializer(user)
        post_serializer = PostSerializer(queryset, context=context, many=True)
        return Response({'posts':post_serializer.data, 'total_posts':total_post,'total_friends': total_friends,'username':user_serializer.data}, status=status.HTTP_200_OK)
    

    def retrieve(self, request, pk=None):
        """
        Handles GET request to retrieve posts of a specific user.

        Args:
            request (Request): HTTP request object containing user data.
            pk (str): Primary key of the user whose posts are to be retrieved.

        Returns:
            Response: JSON response with list of posts and associated data of the specified user.
        """
        context = {"request": request, 'user': request.user}
        user = User.objects.get(pk=pk)
        queryset = Post.objects.filter(user=user).order_by("-created_at")
        total_post = queryset.count()
        total_friends = Friendship.objects.filter(to_user=user,is_accepted =True).count()
        user_serializer = UsernameSerializer(user)
        post_serializer = PostSerializer(queryset, context=context, many=True)

        return Response({'posts':post_serializer.data, 'total_posts':total_post,'total_friends': total_friends,'username':user_serializer.data}, status=status.HTTP_200_OK)

class DeletePostView(viewsets.ViewSet):
    """
    ViewSet for deleting a post.

    Attributes:
        authentication_classes (list): List of authentication classes for verifying user authentication.
    """
    
    authentication_classes = [JWTAuthentication]

    def destroy(self, request, pk=None):
        """
        Handles DELETE request to delete a post.

        Args:
            request (Request): HTTP request object containing user data.
            pk (str): Primary key of the post to be deleted.

        Returns:
            Response: JSON response indicating success or failure of post deletion.
        """
        post = Post.objects.filter(pk=pk, user=request.user.id)
        if post:
            post.delete()
            return Response({"msg": "Post Deleted"}, status=status.HTTP_201_CREATED)
        return Response(
            {"msg": "Post Not Found"}, status=status.HTTP_404_NOT_FOUND
        )

class LikePostView(viewsets.ViewSet):
    """
    ViewSet for liking/unliking a post.

    Attributes:
        authentication_classes (list): List of authentication classes for verifying user authentication.
    """
    
    authentication_classes = [JWTAuthentication]

    def retrieve(self, request, pk=None):
        """
        Handles GET request to like/unlike a post.

        Args:
            request (Request): HTTP request object containing user data.
            pk (str): Primary key of the post to be liked/unliked.

        Returns:
            Response: JSON response indicating success or failure of like/unlike operation.
        """
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                {"msg": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        like, created = Like.objects.get_or_create(post=post, user=request.user,is_like=False)

        if created:
            return Response({"msg": "Liked Post"}, status=status.HTTP_201_CREATED)
        else:
            if like.is_like:
                like.is_like = False
                like.save()
                return Response({"msg": "Unliked Post"}, status=status.HTTP_200_OK)
            else:
                like.is_like = True
                like.save()
                return Response({"msg": "Liked Post"}, status=status.HTTP_200_OK)

class AddCommentView(viewsets.ViewSet):
    """
    ViewSet for adding comments to a post.

    Attributes:
        authentication_classes (list): List of authentication classes for verifying user authentication.
    """
    
    authentication_classes = [JWTAuthentication]

    def create(self, request):
        """
        Handles POST request to add a comment to a post.

        Args:
            request (Request): HTTP request object containing user data and comment content.

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

class FriendRequestSendView(viewsets.ViewSet):
    """
    ViewSet for sending friend requests to other users.

    Attributes:
        authentication_classes (list): List of authentication classes for verifying user authentication.
    """
    
    authentication_classes = [JWTAuthentication]

    def retrieve(self, request, pk=None):
        """
        Handles GET request to send a friend request to another user.

        Args:
            request (Request): HTTP request object containing user data.
            pk (str): Primary key of the user to whom the friend request is sent.

        Returns:
            Response: JSON response indicating success or failure of friend request sending.
        """
        try:
            to_user = get_object_or_404(User, pk=pk)
            friend_request = Friendship.objects.filter(
                from_user=request.user, to_user=to_user
            ).first()

            if friend_request is None:
                friend_request = Friendship.objects.create(
                    from_user=request.user, to_user=to_user
                )
                return Response(
                    {"msg": "Friend request sent"}, status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {"msg": "Friend request already sent"}, status=status.HTTP_200_OK
                )

        except User.DoesNotExist:
            return Response(
                {"msg": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

class FriendRequestAcceptView(viewsets.ViewSet):
    """
    ViewSet for accepting friend requests.

    Attributes:
        authentication_classes (list): List of authentication classes for verifying user authentication.
    """
    
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        """
        Handles GET request to list pending friend requests.

        Args:
            request (Request): HTTP request object containing user data.

        Returns:
            Response: JSON response with list of pending friend requests.
        """
        context = {"request": request}
        friend_request = Friendship.objects.filter(to_user=request.user, is_accepted=False)

        friend_request_serializer = FriendshipRequestSerializer(
            friend_request, context=context, many=True
        )
        return Response(friend_request_serializer.data)

    def retrieve(self, request, pk=None):
        """
        Handles GET request to accept a friend request.

        Args:
            request (Request): HTTP request object containing user data.
            pk (str): Primary key of the friend request to be accepted.

        Returns:
            Response: JSON response indicating success or failure of friend request acceptance.
        """
        try:
            pk = json.loads(pk)
            friendrequest = Friendship.objects.get(pk=pk, to_user=request.user)
            if not friendrequest.is_accepted:
                friendrequest.is_accepted = True
                friendrequest.save()
                return Response(
                    {"msg": "Request accepted"}, status=status.HTTP_201_CREATED
                )
            return Response(
                {"msg": "Request already accepted"}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"msg": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

class UnfollowFriendRequestView(viewsets.ViewSet):
    """
    ViewSet for unfollowing/rejecting friend requests.

    Attributes:
        authentication_classes (list): List of authentication classes for verifying user authentication.
    """
    
    authentication_classes = [JWTAuthentication]
            
    def destroy(self, request, pk=None):
        """
        Handles DELETE request to unfollow/reject a friend request.

        Args:
            request (Request): HTTP request object containing user data.
            pk (str): Primary key of the user to unfollow/reject.

        Returns:
            Response: JSON response indicating success or failure of unfollow/rejection.
        """
        friendrequest = Friendship.objects.filter(Q(from_user=request.user, to_user=pk) | Q(from_user=pk, to_user=request.user)).first()
        if friendrequest:
            friendrequest.delete()
            return Response(
                {"msg": "Friend request rejected"}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"msg": "Friendship Not Found"}, status=status.HTTP_404_NOT_FOUND
        )

class RejectFriendRequestView(viewsets.ViewSet):
    """
    ViewSet for rejecting friend requests.

    Attributes:
        authentication_classes (list): List of authentication classes for verifying user authentication.
    """
    
    authentication_classes = [JWTAuthentication]

    def destroy(self, request, pk=None):
        """
        Handles DELETE request to reject a friend request.

        Args:
            request (Request): HTTP request object containing user data.
            pk (str): Primary key of the friend request to be rejected.

        Returns:
            Response: JSON response indicating success or failure of friend request rejection.
        """
        reject_friend_request = Friendship.objects.filter(
            pk=pk, to_user=request.user.id
        )
        if reject_friend_request:
            reject_friend_request.delete()
            return Response(
                {"msg": "Friend request rejected"}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"msg": "Friendship Not Found"}, status=status.HTTP_404_NOT_FOUND
        )
