"""
This module contains serializer for passing data into json format.
"""

from rest_framework import serializers
from .models import (
    Conversation,
    Message,
)
from Users.models import User
from urllib.parse import urljoin

class UserDataSerializer(serializers.ModelSerializer):
    profile_image=serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username',"first_name","last_name","profile_image"]
    
    def get_profile_image(self, obj):
        request = self.context.get('request')
        profile_image = obj.profile_img

        if profile_image and request:

            return urljoin(request.build_absolute_uri('/'), profile_image.url)

        return None

class SendConversationSerializer(serializers.ModelSerializer):
    
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_name', 'participants']

    def get_participants(self, obj):
        request = self.context.get('request', None)
        if request:
            logged_in_user = request.user
            participants = obj.participants.exclude(id=logged_in_user.id)
            return UserDataSerializer(participants,context=self.context, many=True).data
        return UserDataSerializer(obj.participants, many=True).data

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["conversation_name"]

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("sender", "text", "sender", "conversation_id")

        def create(self, validated_data):
            message = Message.objects.create(
                sender=validated_data["sender"],
                text=validated_data["text"],
                conversation_id=validated_data["conversation_id"],
            )
            return message