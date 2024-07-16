from django.contrib import admin
from .models import Conversation, Message, Notification
# Register your models here.
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    This class displays Conversation Between Users in the admin panel.
    """

    list_display = ["id", "conversation_name"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    This class displays messages in the admin panel.
    """

    list_display = ["id", "conversation", "sender", "text"]

