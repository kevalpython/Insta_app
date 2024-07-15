from django.shortcuts import render
from .models import Conversation
from .serializers import ConversationSerializer, SendConversationSerializer
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from Users.models import User
from django.db.models import Q
from Posts.management.authentication import JWTAuthentication


class ConversationView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        user = request.user.id
        context = {"request": request}
        conversations = Conversation.objects.filter(participants__id=user)
        conversation_serializer = SendConversationSerializer(
            conversations, context=context, many=True
        )
        return Response(conversation_serializer.data)

    def retrieve(self, request, pk=None):
        try:

            receiver_id = pk

            sender_id = request.user.id

            sender_conv_name = f"{User.objects.get(pk=sender_id).username}_{User.objects.get(pk=receiver_id).username}"

            receiver_conv_name = f"{User.objects.get(pk=receiver_id).username}_{User.objects.get(pk=sender_id).username}"

            conversation = Conversation.objects.filter(
                Q(conversation_name=sender_conv_name, participants__id=pk)
                | Q(conversation_name=receiver_conv_name, participants__id=sender_id)
            ).first()

            if not conversation:
                conversation_create = Conversation.objects.create(
                    conversation_name=receiver_conv_name
                )
                conversation_create.participants.add(sender_id, receiver_id)
            if conversation:
                conversation_serializer = ConversationSerializer(conversation)
            else:
                conversation_serializer = ConversationSerializer(conversation_create)
            return Response(
                {
                    "msg": (
                        "conversation already exists"
                        if conversation
                        else "conversation created"
                    ),
                    "conversation_name": conversation_serializer.data,
                },
                status=status.HTTP_200_OK if conversation else status.HTTP_201_CREATED,
            )
        except User.DoesNotExist:
            return Response(
                {"msg": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"msg": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
