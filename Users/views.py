"""
This module contains views for user management and authentication.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .models import User
from .serializers import RegisterSerializer, UserSerializer, UserLoginSerializer, UserSearchSerializer
import jwt
from django.conf import settings
from Posts.management.authentication import JWTAuthentication
from rest_framework import filters


class RegisterView(viewsets.ViewSet):
    """
    ViewSet for user registration.
    """

    permission_classes = (AllowAny,)

    def create(self, request):
       
        """
        Handles user registration.

        Args:
            request (Request): HTTP request containing user registration data.

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

    Args:
        user (User): User instance for which tokens are generated.

    Returns:
        dict: Dictionary containing encoded access and refresh tokens.
    """
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    # Convert the tokens to strings before encoding
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

        Args:
            request (Request): HTTP request containing user login credentials.

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
    

class UserProfileView(viewsets.ViewSet):
    """
    ViewSet for managing user profiles.
    """

    queryset = User.objects.all()
    authentication_classes = [JWTAuthentication]
    serializer_class = UserSerializer

    def list(self, request):
        """
        Lists all user profiles.

        Args:
            request (Request): HTTP request.

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
        context = {'request': request}
        user = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(user, context=context)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        """
        Partially updates a user profile.

        Args:
            request (Request): HTTP request containing updated user data.
            pk (int): Primary key of the user profile to update.

        Returns:
            Response: JSON response indicating success or failure of the update operation.
        """
        user = get_object_or_404(self.queryset, pk=pk)
        if user != request.user:
            return Response({"msg": "User permission denied"}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        serializer = UserSerializer(user, data=request.data, context=request.user, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "User Updated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Deletes a user profile.

        Args:
            request (Request): HTTP request.
            pk (int): Primary key of the user profile to delete.

        Returns:
            Response: JSON response indicating success or failure of the delete operation.
        """
        user = get_object_or_404(self.queryset, pk=pk)
        if user.profile_img:
            import os
            import shutil
            if os.path.isfile(user.profile_img.path):
                shutil.rmtree(f'media/images/{user.username}')
        user.delete()
        return Response({"msg": "User Deleted"}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    API view for user logout.
    """

    authentication_classes = [JWTAuthentication]

    def post(self, request):
        """
        Handles user logout by invalidating tokens.

        Args:
            request (Request): HTTP request containing refresh token to invalidate.

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
    
    def get_serializer_context(self):
        """
        Provides the context for the serializer.

        Returns:
            dict: Dictionary containing the request object.
        """
        return {'request': self.request}
