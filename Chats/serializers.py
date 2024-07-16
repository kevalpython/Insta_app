"""
Serializers for converting Django model instances to JSON format.
"""

from rest_framework import serializers
from .models import (
    Conversation,
    Message,
)
from Users.models import User
from urllib.parse import urljoin

class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializer for User model to include user data with profile image URL.

    Attributes:
        profile_image (SerializerMethodField): Method field to get the profile image URL.
    """
    
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_image']
    
    def get_profile_image(self, obj):
        """
        Method to get the profile image URL for a user.

        Args:
            obj (User): The User instance.

        Returns:
            str or None: The profile image URL if available, otherwise None.
        """
        request = self.context.get('request')
        profile_image = obj.profile_img

        if profile_image and request:
            return urljoin(request.build_absolute_uri('/'), profile_image.url)

        return None

class SendConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model to include conversation data with participants' user data.

    Attributes:
        participants (SerializerMethodField): Method field to get participants' user data.
    """

    participants = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_name', 'participants']

    def get_participants(self, obj):
        """
        Method to get participants' user data for a conversation.

        Args:
            obj (Conversation): The Conversation instance.

        Returns:
            list: Serialized data of participants' user data.
        """
        request = self.context.get('request', None)
        if request:
            logged_in_user = request.user
            participants = obj.participants.exclude(id=logged_in_user.id)
            return UserDataSerializer(participants, context=self.context, many=True).data
        return UserDataSerializer(obj.participants, many=True).data

class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model to include basic conversation data.

    This serializer is used for basic representation of Conversation model.

    Attributes:
        Meta (class): Meta class specifying the model and fields to include.
    """
    
    class Meta:
        model = Conversation
        fields = ["conversation_name"]

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model to include message data.
    """
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ("sender_username", "text", "conversation")

    def create(self, validated_data):
        """
        Method to create a new Message instance.
        """
        message = Message.objects.create(
            sender=validated_data["sender"],
            text=validated_data["text"],
            conversation=validated_data["conversation"],
        )
        return message
