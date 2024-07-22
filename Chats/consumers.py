"""
This module defines the ChatConsumer class, which handles WebSocket connections for chat functionality.
The consumer manages connection, authentication via JWT tokens, message retrieval, and real-time message broadcasting.
"""

import json
import jwt
from urllib.parse import parse_qs
from django.db.models import Q
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from .models import Message, Conversation, Notification
from .serializers import MessageSerializer
from Users.models import User


def verify_jwt_token(token):
    """
    Verifies the JWT token to authenticate the user.

    Args:
        token (str): The JWT token.

    Returns:
        User: The authenticated user, or None if the token is invalid or expired.
    """
    try:
        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        decode_access = jwt.decode(
            decoded_payload["access"], settings.SECRET_KEY, algorithms=["HS256"]
        )
        user_id = decode_access["id"]
        user = User.objects.get(id=user_id)
        return user
    except jwt.ExpiredSignatureError:
        return None
    except (jwt.InvalidTokenError, User.DoesNotExist):
        return None


class ChatConsumer(AsyncWebsocketConsumer):
    """
    A consumer to handle WebSocket connections for chat functionality.

    Attributes:
        user (User or AnonymousUser): The user connecting to the WebSocket.
        conversation_name (str): The name of the conversation room.
        room_group_name (str): The name of the channel layer group.
    """

    async def connect(self):
        """
        Handles the connection event when a client attempts to connect to the WebSocket.
        Verifies the JWT token, adds the user to the channel layer group, and sends the chat history.
        """
        query_string = self.scope["query_string"].decode()
        query_params = parse_qs(query_string)
        token_key = query_params.get("token", [None])[0]

        if token_key:
            self.user = verify_jwt_token(token_key)
        else:
            self.user = AnonymousUser()

        if self.user.is_authenticated:
            self.conversation_name = self.scope["url_route"]["kwargs"][
                "conversation_name"
            ]
            self.room_group_name = f"chat_{self.conversation_name}"

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

            conversation = await self.get_conversation(self.conversation_name)
            messages = await self.get_messages(conversation)
            un_seen_mesasages = await self.get_unseen_messages(conversation, self.user)
            message_serializer = MessageSerializer(messages, many=True)

            await self.send(text_data=json.dumps(message_serializer.data))
        else:
            await self.close()

    async def disconnect(self, close):
        """
        Handles the disconnection event when a client disconnects from the WebSocket.

        """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Handles receiving messages from the WebSocket.

        Args:
            text_data (str): The received message data in JSON format.
        """
        sender_id = self.user.id
        text_data = json.loads(text_data)
        try:
            conversation = await self.get_conversation(self.conversation_name)
            new_message = await self.save_message(sender_id, text_data, conversation)

            message_serializer = MessageSerializer(new_message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat.message", "message": message_serializer.data},
            )
        except Exception as e:
            print(f"Error in receive method: {str(e)}")
            raise e

    @database_sync_to_async
    def get_conversation(self, room_name):
        """
        Retrieves the conversation object based on the room name.

        Args:
            room_name (str): The name of the conversation room.

        Returns:
            Conversation: The conversation object.
        """
        return Conversation.objects.get(conversation_name=room_name)

    @database_sync_to_async
    def save_message(self, sender_id, message, conversation):
        """
        Saves a new message to the database.

        Args:
            sender_id (int): The ID of the user sending the message.
            message (dict): The message data.
            conversation (Conversation): The conversation object.

        Returns:
            Message: The saved message object.
        """

        sender = User.objects.get(pk=sender_id)
        new_message = Message.objects.create(
            sender=sender, text=message, conversation=conversation
        )
        conversation = Conversation.objects.get(conversation_name=conversation)
        recipients = conversation.participants.exclude(pk=sender.pk)
        for user in recipients:
            Notification.objects.create(message=new_message, user=user)
        return new_message

    @database_sync_to_async
    def get_messages(self, conversation):
        """
        Retrieves all messages for a given conversation, ordered by creation time.

        Args:
            conversation (Conversation): The conversation object.

        Returns:
            QuerySet: The list of message objects.
        """
        return Message.objects.filter(conversation=conversation).order_by("created_at")

    @database_sync_to_async
    def get_unseen_messages(self, conversation, username):
        """
        Retrieves the conversation object based on the room name.

        Args:
            room_name (str): The name of the conversation room.

        Returns:
            Conversation: The conversation object.
        """
        unseen_message = Message.objects.filter(
            conversation=conversation, is_seen=False
        ).exclude(sender=username)
        for i in unseen_message:
            i.is_seen = True
            i.save()
            notifiction_seen = Notification.objects.filter(
                message=i, user__username=username
            )
            for notification in notifiction_seen:
                notification.is_seen = True
                notification.save()

        return "seen"

    async def chat_message(self, event):
        """
        Sends a chat message to the WebSocket.

        Args:
            event (dict): The event data containing the message.
        """
        try:
            await self.send(text_data=json.dumps(event["message"]))
        except Exception as e:
            print(f"Error in chat_message method: {str(e)}")
            raise e


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope["url_route"]["kwargs"]["username"]
        await self.channel_layer.group_add(self.username, self.channel_name)        
        await self.accept()
        count = await self.get_notifications(self.username)
        await self.send(text_data=json.dumps({"count": count}))

    async def disconnect(self, close_code):
        """
        Handles the disconnection event when a client disconnects from the WebSocket.

        Args:
            close_code (int): The close code for the disconnection.
        """
        await self.channel_layer.group_discard(self.username, self.channel_name)

    async def send_notification(self, event):
        data = json.loads(event.get("value"))
        count = data["count"]
        await self.send(text_data=json.dumps({"count": count}))

    @database_sync_to_async
    def get_notifications(self, username):
        """
        Retrieves all messages for a given conversation, ordered by creation time.

        Args:
            conversation (Conversation): The conversation object.

        Returns:
            QuerySet: The list of message objects.
        """
        return Notification.objects.filter(
            user__username=username, is_seen=False
        ).count()


class ConversationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope["query_string"].decode()
        query_params = parse_qs(query_string)
        token_key = query_params.get("token", [None])[0]

        if token_key:
            self.user = verify_jwt_token(token_key)
        else:
            self.user = AnonymousUser()
        if not self.user.is_authenticated:
            await self.close()
        self.conversation_name = self.scope["url_route"]["kwargs"]["conversation_name"]
        self.group_name = f"messages_{self.conversation_name}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        try:
            conversation = Conversation.objects.get(
                conversation_name=self.conversation_name
            )
        except Conversation.DoesNotExist:
            await self.close()
            return

        messages = Message.objects.filter(
            conversation=conversation, is_seen=False
        ).exclude(sender=self.user)

        await self.send(text_data=json.dumps({"count": messages.count()}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_messge_notification_count(self, event):
        data = json.loads(event.get("value"))
        count = data["message_useen_count"]
        await self.send(text_data=json.dumps({"count": count}))
