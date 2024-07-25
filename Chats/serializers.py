"""
This module contains serializer for passing data into json format.
"""

from rest_framework import serializers
from .models import (
    Conversation,
    Message,
)

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