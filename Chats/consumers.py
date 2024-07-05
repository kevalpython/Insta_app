import json
import jwt
from urllib.parse import parse_qs
from django.db.models import Q
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from .models import Message, Conversation
from .serializers import MessageSerializer
from Users.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("hiiii")
        query_string = self.scope["query_string"].decode()
        query_params = parse_qs(query_string)
        token_key = query_params.get("token", [None])[0]

        if token_key:
            self.user = await self.verify_jwt_token(token_key)
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
            message_serializer = MessageSerializer(messages, many=True)

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat.message", "message": message_serializer.data},
            )
        else:
            await self.close()

    async def verify_jwt_token(self, token):
        try:
            decoded_payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            user_id = decoded_payload["id"]
            user = User.objects.get(id=user_id)
            return user
        except jwt.ExpiredSignatureError:
            return None  
        except (jwt.InvalidTokenError, User.DoesNotExist):
            return None  

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data):

        sender_id = self.user.id

        try:
            conversation = await self.get_conversation(self.conversation_name)

            await self.save_message(sender_id, text_data, conversation)

            messages = await self.get_messages(conversation)
            message_serializer = MessageSerializer(messages, many=True)

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat.message", "message": message_serializer.data},
            )

        except Exception as e:
            print(f"Error in receive method: {str(e)}")
            raise e

    @database_sync_to_async
    def get_conversation(self, room_name):
        return Conversation.objects.get(conversation_name=room_name)

    @database_sync_to_async
    def save_message(self, sender_id, message, conversation):
        sender = User.objects.get(pk=sender_id)
        new_message = Message.objects.create(
            sender=sender, text=message, conversation=conversation
        )
        return new_message

    @database_sync_to_async
    def get_messages(self, conversation):
        return Message.objects.filter(conversation=conversation)

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps(event["message"]))
        except Exception as e:
            print(f"Error in chat_message method: {str(e)}")
            raise e
