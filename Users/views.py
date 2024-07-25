from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import  User
from .serializers import RegisterSerializer,UserSerializer,UserLoginSerializer

class RegisterView(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def create(self, request):
        print("request = ",request.data)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "User Created"},status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    print(str(refresh))
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserLoginView(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                user_serializer = UserSerializer(user)
                return Response({'msg':'Login Successful.', 'token':token, "user":user_serializer.data }, status=status.HTTP_200_OK)
            return Response({'msg':'Invalid Credential.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    
class UserProfileView(viewsets.ViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        context={'request':request}
        user = get_object_or_404(self.queryset,pk=pk)
        serializer = self.serializer_class(user,context=context)
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


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)