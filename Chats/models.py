"""
Models for handling chat conversations and messages.
"""

from django.db import models
from core.models import BaseModel
from Users.models import User

class Conversation(BaseModel):
    """
    A model representing a conversation between multiple users.

    Attributes:
        conversation_name (str): The name of the conversation.
        participants (ManyToManyField): The users participating in the conversation.
    """
    
    conversation_name = models.TextField(blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='conversations')

    def __str__(self) -> str:
        """
        Returns a string representation of the conversation.

        Returns:
            str: The name of the conversation.
        """
        return self.conversation_name


class Message(BaseModel):
    """
    A model representing a message in a conversation.

    Attributes:
        conversation (ForeignKey): The conversation to which the message belongs.
        sender (ForeignKey): The user who sent the message.
        text (str): The content of the message.
    """
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField()
    is_seen = models.BooleanField(default=False)
    def __str__(self) -> str:
        """
        Returns a string representation of the message.

        Returns:
            str: The content of the message.
        """
        return self.text


class Notification(BaseModel):
    """
    A model representing a notifictions of messages.
    
    Attributes:
        
    """
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name= 'notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    is_seen = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return self.user.username
    