from .models import *
from .serializers import (
    PostSerializer,
    CommentSerializer,
    FriendshipRequestSerializer,
)
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404


class AddPostView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        data = {
            "user": request.user.id,
            "content": request.data["content"],
            "file": request.data["files"],
        }

        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        user = self.request.user
        friends_ids = Friendship.objects.filter(
            from_user=user, is_accepted=True
        ).values_list("to_user", flat=True)
        # Retrieve the queryset of posts for the current user and their friends
        posts = Post.objects.filter(Q(user=user) | Q(user__in=friends_ids)).order_by(
            "-created_at"
        )

        # Serialize the queryset into data using PostSerializer
        post_serializer = PostSerializer(
            posts, many=True
        )  # Use many=True because queryset contains multiple items

        return Response(post_serializer.data, status=status.HTTP_200_OK)


class PostView(viewsets.ViewSet):

    def list(self, request):
        user = self.request.user
        queryset = Post.objects.filter(user=user).order_by("-created_at")
        post_serializer = PostSerializer(queryset, many=True)
        return Response(post_serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        Retrieve a single blog with its associated comments.

        Args:
            request: The request object.
            pk (int): The primary key of the blog.

        Returns:
            Response: A serialized blog along with its comments.
        """
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        post_serializer = PostSerializer(post)

        return Response(
            {
                "post": post_serializer.data,
            }
        )


class DeletePostView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, pk=None):
        post = Post.objects.filter(pk=pk, user=request.user.id)
        if post:
            post.delete()
            return Response({"msg": "Post Deleted"}, status=status.HTTP_201_CREATED)
        return Response(
            {"msg": "Post Not Found"}, status_code=status.HTTP_404_NOT_FOUND
        )


class LikePostView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                {"msg": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        like, created = Like.objects.get_or_create(post=post, user=request.user)

        if created:
            like.is_like = True
            like.save()
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
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        data = {
            "post": request.data["post"],
            "user": request.user.id,
            "content": request.data["content"],
        }
        add_post_serializer = CommentSerializer(data=data)
        if add_post_serializer.is_valid():
            add_post_serializer.save()
            return Response({"msg": "Comment Created"}, status=status.HTTP_201_CREATED)
        return Response(add_post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FriendRequestSendView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
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
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        friend_request = Friendship.objects.filter(to_user=request.user)
        friend_request_serializer = FriendshipRequestSerializer(
            friend_request, many=True
        )
        return Response(friend_request_serializer.data)

    def retrieve(self, request, pk=None):
        try:
            friendrequest = Friendship.objects.get(pk=pk, to_user=request.user)
            if friendrequest.is_accepted == False:
                friendrequest.is_accepted = True
                friendrequest.save()
                print(friendrequest)
                return Response(
                    {"msg": "Request accepted"}, status=status.HTTP_201_CREATED
                )
            return Response(
                {"msg": "Request already accepted"}, status=status.HTTP_201_CREATED
            )
        except User.DoesNotExist:
            return Response(
                {"msg": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


class UnfollowFriendRequestView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        try:
            friendrequest = Friendship.objects.get(pk=pk)
            if friendrequest.is_accepted == True:
                friendrequest.is_accepted = False
                friendrequest.save()
                print(friendrequest)
                return Response(
                    {"msg": "User Unfollowed"}, status=status.HTTP_201_CREATED
                )
            return Response(
                {"msg": "User already Unfollowed"}, status=status.HTTP_201_CREATED
            )
        except User.DoesNotExist:
            return Response(
                {"msg": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


class RejectFriendRequestView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, pk=None):
        reject_friend_request = Friendship.objects.filter(
            pk=pk, to_user=request.user.id
        )
        if reject_friend_request:
            reject_friend_request.delete()
            return Response(
                {"msg": "Friend request rejected"}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"msg": "Friendship Not Found"}, status_code=status.HTTP_404_NOT_FOUND
        )
