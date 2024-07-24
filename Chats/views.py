"""
Viewset for handling conversation-related operations.
"""

from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.response import Response

from Posts.management.authentication import JWTAuthentication
from Users.models import User

from .models import Conversation
from .serializers import ConversationSerializer, SendConversationSerializer


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
        Marks all notifications related to conversations as seen.

        Returns:
            Response: JSON response containing serialized conversation data.
        """
        user_id = request.user.id
        conversations = Conversation.objects.filter(participants__id=user_id)
        serializer = SendConversationSerializer(conversations, context={"request": request}, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieves a specific conversation between the authenticated user and another user.
        If the conversation does not exist, creates a new conversation.

        Returns:
            Response: JSON response containing the conversation data and status.
        """
        sender_id = request.user.id
        try:
            receiver = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"msg": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        sender_username = request.user.username
        receiver_username = receiver.username

        conv_names = [
            f"{sender_username}_{receiver_username}",
            f"{receiver_username}_{sender_username}"
        ]

        conversation = Conversation.objects.filter(
            Q(conversation_name=conv_names[0]) | Q(conversation_name=conv_names[1])
        ).first()

        if not conversation:
            conversation = Conversation.objects.create(conversation_name=conv_names[1])
            conversation.participants.set([sender_id, receiver.id])
            msg = "conversation created"
            status_code = status.HTTP_201_CREATED
        else:
            msg = "conversation already exists"
            status_code = status.HTTP_200_OK

        serializer = ConversationSerializer(conversation)
        return Response({"msg": msg, "conversation_name": serializer.data}, status=status_code)
