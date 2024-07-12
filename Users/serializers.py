
"""
This module contains serializer for passing data into json format.
"""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from Posts.models import Friendship
from .models import User
from django.db.models import Q

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "password2",
            "email",
            "first_name",
            "last_name",
            "profile_img",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            profile_img = validated_data["profile_img"],
        )
        user.set_password(validated_data["password"])
        user.save()

        return user
    
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """

    class Meta:
        """
        Metadata options for the UserSerializer.
        """

        model = User
        fields = "__all__"
        
    def validate(self, attrs):
        
        return super().validate(attrs)


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)
    class Meta:
        model = User
        fields = ['username', 'password']


class UserSearchSerializer(serializers.ModelSerializer):
    friend_request = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'profile_img', 'first_name', 'last_name', 'friend_request']
        
    def get_friend_request(self, obj):
        # Get the current user from the request context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            friendship = Friendship.objects.filter(Q(from_user=request.user, to_user=obj.id) | Q(from_user=obj.id, to_user=request.user)).first()
            if friendship:
                if friendship.is_accepted:
                    return "accepted"
                return "requested"
        return "not"
    