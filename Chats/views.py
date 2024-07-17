"""
Viewset for handling conversation-related operations.
"""
from .models import Conversation,Notification
from .serializers import ConversationSerializer, SendConversationSerializer
from rest_framework import status, viewsets
from rest_framework.response import Response
from Users.models import User
from django.db.models import Q
from Posts.management.authentication import JWTAuthentication

class ConversationView(viewsets.ViewSet):
    """
    Viewset for handling conversation-related operations.

    Attributes:
        authentication_classes (list): List of authentication classes used for viewset.
    """

    authentication_classes = [JWTAuthentication]

    def list(self, request):
        """
        Retrieves a list of conversations for the authenticated user.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: JSON response containing serialized conversation data.
        """
        user = request.user.id
        context = {"request": request}
        conversations = Conversation.objects.filter(participants__id=user)
        conversation_serializer = SendConversationSerializer(
            conversations, context=context, many=True
        )
        notification=Notification.objects.filter(user=request.user,is_seen=False)
        for i in notification:
            i.is_seen=True
            i.save()
        return Response(conversation_serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieves a specific conversation between the authenticated user and another user.

        Args:
            request (Request): The HTTP request object.
            pk (str): The primary key of the user with whom the conversation is retrieved.

        Returns:
            Response: JSON response containing the conversation data and status.
        """
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
