from django.db import models
from core.models import BaseModel
from Users.models import User

# Create your models here.
class Conversation(BaseModel):
    """
        Conversation models tract conversaction_id between Multiple Users
    """

    conversation_name = models.TextField(blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='conversations')

    def __str__(self) -> str:
        return self.conversation_name

class Message(BaseModel):
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField()
    
    def __str__(self) -> str:
        return self.text


