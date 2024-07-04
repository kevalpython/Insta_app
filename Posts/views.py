from django.shortcuts import render
from .models import *
from .serializers import (
    PostSerializer,
    ImageVideoSerializer,
    IsLikeSerializer,
    CommentSerializer,
    # ConversationSerializer,
    # MessageSerializer,
)
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# Create your views here.


class AddPostView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def create(self, request):
        user = request.user.id
        files = dict((request.data).lists())["files"]
        data = {"user": user, "content": request.data["content"]}
        add_post_serializer = PostSerializer(data=data)
        if add_post_serializer.is_valid():
            post = add_post_serializer.save()
            if files:
                for file in files:
                    image_data = {"user": user, "file": file, "post": post.id}
                    image_serialzer = ImageVideoSerializer(data=image_data)
                    if image_serialzer.is_valid():
                        image_serialzer.save()
            return Response({"msg": "Post Created", "status": status.HTTP_201_CREATED})
        return Response(add_post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostView(viewsets.ViewSet):

    def list(self, request):
        posts = Post.objects.filter(user=request.user.id)

        data = []
        for post in posts:
            image_video = PostImageVideo.objects.filter(post=post)
            post_serializer = PostSerializer(post)
            image_video_serializer = ImageVideoSerializer(image_video, many=True)
            data.append(
                {
                    "post": post_serializer.data,
                    "image_video": image_video_serializer.data,
                }
            )
        return Response(data)

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
        image_video = PostImageVideo.objects.filter(post=post)
        image_video_serializer = ImageVideoSerializer(image_video, many=True)
        like = Like.objects.filter(post=post)
        is_like = Like.objects.get(user=request.user.id)
        is_like_serializer = IsLikeSerializer(is_like)
        total_like = like.count()
        return Response(
            {
                "post": post_serializer.data,
                "image_video": image_video_serializer.data,
                "total_likes": total_like,
                "is_like": is_like_serializer.data["is_like"],
            }
        )


class DeletePostView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, pk=None):
        post = Post.objects.filter(pk=pk, user=request.user.id)
        if post:
            post.delete()
            return Response({"msg": "Post Deleted", "status": status.HTTP_201_CREATED})
        return Response(
            {"msg": "Post Not Found", "status_code": status.HTTP_404_NOT_FOUND}
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
            return Response({"msg": "Liked Post", "status": status.HTTP_201_CREATED})
        else:
            if like.is_like:
                like.is_like = False
                like.save()
                return Response({"msg": "Unliked Post", "status": status.HTTP_200_OK})
            else:
                like.is_like = True
                like.save()
                return Response({"msg": "Liked Post", "status": status.HTTP_200_OK})


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
            return Response({"msg": "Post Created", "status": status.HTTP_201_CREATED})
        return Response(add_post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
