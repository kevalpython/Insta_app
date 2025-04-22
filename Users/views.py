"""
This module contains views for user management and authentication.
"""

from rest_framework import viewsets, status, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import jwt
import os
import shutil

from .serializers import RegisterSerializer, UserLoginSerializer, UserSerializer, UserSearchSerializer
from .models import User

from Posts.management.authentication import JWTAuthentication

class RegisterView(viewsets.ViewSet):
    """
    ViewSet for user registration.
    """

    permission_classes = (AllowAny,)

    def create(self, request):
       
        """
        Handles user registration.

        Returns:
            Response: JSON response indicating success or failure of registration.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "User Created"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_tokens_for_user(user):
    """
    Generates access and refresh tokens for a given user.

    Returns:
        dict: Dictionary containing encoded access and refresh tokens.
    """
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    
    refresh_encoded = jwt.encode({"refresh": str(refresh)}, settings.SECRET_KEY, algorithm="HS256")
    access_encoded = jwt.encode({"access": str(access)}, settings.SECRET_KEY, algorithm="HS256")

    return {
        'refresh': refresh_encoded,
        'access': access_encoded,
    }


class UserLoginView(APIView):
    """
    API view for user login.
    """

    def post(self, request, format=None):
        """
        Handles user login.

        Returns:
            Response: JSON response containing login status, tokens, and user data.
        """
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
    

class UserProfileView(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles and searching users.
    """

    queryset = User.objects.all()
    authentication_classes = [JWTAuthentication]
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'search' and self.request.user.is_authenticated:
            queryset = queryset.exclude(pk=self.request.user.pk)
        return queryset

    def list(self, request):
        """
        Lists all user profiles.

        Returns:
            Response: JSON response containing serialized user profiles.
        """
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieves a specific user profile.

        Args:
            request (Request): HTTP request.
            pk (int): Primary key of the user profile to retrieve.

        Returns:
            Response: JSON response containing serialized user profile.
        """
        user = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        """
        Partially updates a user profile.

        Returns:
            Response: JSON response indicating success or failure of the update operation.
        """
        user = get_object_or_404(self.queryset, pk=pk)
        if user != request.user:
            return Response({"msg": "User permission denied"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(user, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "User Updated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Deletes a user profile.

        Returns:
            Response: JSON response indicating success or failure of the delete operation.
        """
        user = get_object_or_404(self.queryset, pk=pk)
        password = request.data.get('password')
        
        if not password:
            return Response({"msg": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not check_password(password, user.password):
            return Response({"msg": "Password incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.profile_img and os.path.isfile(user.profile_img.path):
            shutil.rmtree(f'media/images/{user.username}')

        user.delete()
        return Response({"msg": "User Deleted"}, status=status.HTTP_200_OK)

    def search(self, request):
        """
        Searches for users based on username, first name, or last name.

        Returns:
            Response: JSON response containing the search results.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = UserSearchSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class LogoutView(APIView):
    """
    API view for user logout.
    """

    authentication_classes = [JWTAuthentication]

    def post(self, request):
        """
        Handles user logout by invalidating tokens.

        Returns:
            Response: JSON response indicating success or failure of the logout operation.
        """
        try:
            refresh_token = request.data["refresh_token"]
            decode_refresh = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
            token = RefreshToken(decode_refresh["refresh"])
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class SearchUserView(viewsets.ModelViewSet):
    """
    ViewSet for searching users based on username, first name, or last name.
    """

    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSearchSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name']
    
    def get_queryset(self):
        queryset = User.objects.all()
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(pk=self.request.user.pk)
        return queryset
    
    def get_serializer_context(self):
        """
        Provides the context for the serializer.

        Returns:
            dict: Dictionary containing the request object.
        """
        return {'request': self.request}
