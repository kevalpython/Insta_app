from .models import *
import json
from .serializers import (
    PostSerializer,
    CommentSerializer,
    FriendshipRequestSerializer,
    PostImageVideoSerializer,AddPostSerializer,UsernameSerializer
)
from rest_framework import status, viewsets
from Users.serializers import UserSerializer
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .management.authentication import JWTAuthentication # Adjusted import

class AddPostView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    
    def create(self, request):
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
            return Response({"msg": "Post Created"},status=status.HTTP_201_CREATED)
        return Response(add_post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostListView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    def list(self, request):
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
    authentication_classes = [JWTAuthentication]

    def list(self, request):

        context = {"request": request, 'user': request.user}
        user = self.request.user
        queryset = Post.objects.filter(user=user).order_by("-created_at")
        total_post = queryset.count()
        total_friends = Friendship.objects.filter(Q(from_user=user, is_accepted=True) | Q(to_user=user, is_accepted=True)).count()
        print(total_friends)
        user_serializer = UsernameSerializer(user)
        post_serializer = PostSerializer(queryset, context=context, many=True)
        return Response({'posts':post_serializer.data, 'total_posts':total_post,'total_friends': total_friends,'username':user_serializer.data}, status=status.HTTP_200_OK)
    

    def retrieve(self, request, pk=None):
        context = {"request": request, 'user': request.user}
        user = User.objects.get(pk=pk)
        queryset = Post.objects.filter(user=user).order_by("-created_at")
        total_post = queryset.count()
        total_friends = Friendship.objects.filter(to_user=user,is_accepted =True).count()
        user_serializer = UsernameSerializer(user)
        post_serializer = PostSerializer(queryset, context=context, many=True)

        return Response({'posts':post_serializer.data, 'total_posts':total_post,'total_friends': total_friends,'username':user_serializer.data}, status=status.HTTP_200_OK)

class DeletePostView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    def destroy(self, request, pk=None):
        post = Post.objects.filter(pk=pk, user=request.user.id)
        if post:
            post.delete()
            return Response({"msg": "Post Deleted"}, status=status.HTTP_201_CREATED)
        return Response(
            {"msg": "Post Not Found"}, status=status.HTTP_404_NOT_FOUND
        )

class LikePostView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

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
    authentication_classes = [JWTAuthentication]

    def create(self, request):
        data = {
            "post": request.data["post_id"],
            "user": request.user.id,
            "content": request.data["comment"],
        }
        add_post_serializer = CommentSerializer(data=data)
        if add_post_serializer.is_valid():
            add_post_serializer.save()
            print(add_post_serializer.data)
            return Response({"msg": "Comment Created"}, status=status.HTTP_201_CREATED)
        return Response(add_post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FriendRequestSendView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    def retrieve(self, request, pk=None):
        try:
            to_user = get_object_or_404(User, pk=pk)
            print(to_user)
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
                print()
                return Response(
                    {"msg": "Friend request already sent"}, status=status.HTTP_200_OK
                )

        except User.DoesNotExist:
            return Response(
                {"msg": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

class FriendRequestAcceptView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        context = {"request":request}
        friend_request = Friendship.objects.filter(to_user=request.user, is_accepted = False)

        friend_request_serializer = FriendshipRequestSerializer(
            friend_request,context=context, many=True
        )
        print(friend_request_serializer.data)
        return Response(friend_request_serializer.data)

    def retrieve(self, request, pk=None):
        try:
            pk=json.loads(pk)
            
            friendrequest = Friendship.objects.get(pk=pk, to_user=request.user)
            if not friendrequest.is_accepted:
                friendrequest.is_accepted = True
                friendrequest.save()
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
    authentication_classes = [JWTAuthentication]
            
    def destroy(self, request, pk=None):
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
    authentication_classes = [JWTAuthentication]

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
            {"msg": "Friendship Not Found"}, status=status.HTTP_404_NOT_FOUND
        )