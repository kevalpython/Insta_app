

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets

from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import  User
from .serializers import RegisterSerializer

class RegisterView(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def create(self, request):
        print("request = ",request.data)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "User Created", "status": status.HTTP_201_CREATED})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)