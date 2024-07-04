from django.shortcuts import render
from .models import Post
from .serializers import (
    PostSerializer,ImageVideoSerializer
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
