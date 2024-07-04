from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets

from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response

from .models import  User
from .serializers import RegisterSerializer,UserSerializer

class RegisterView(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def create(self, request):
        print("request = ",request.data)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "User Created", "status": status.HTTP_201_CREATED})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateUserView(viewsets.ViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(self.queryset,pk=pk)
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    def partial_update(self, request,pk=None):
        user = get_object_or_404(self.queryset, pk=pk)
        if user != request.user:
            return Response({"msg": "User permission denied", "status": status.HTTP_203_NON_AUTHORITATIVE_INFORMATION})
        serializer = UserSerializer(user,data=request.data,context=request.user,partial=True)
        if serializer.is_valid():
            serializer.save()   
            return Response({"msg": "User Updated", "status": status.HTTP_201_CREATED})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        print("request =",request.data)
        user = get_object_or_404(self.queryset, pk=pk)
        if user.profile_img:
            import os
            import shutil
            if os.path.isfile(user.profile_img.path):
                shutil.rmtree(f'media/images/{user.username}')
        user.delete()
        return Response({"msg": "User Deleted", "status": status.HTTP_201_CREATED})

