"""
Viewset for handling conversation-related operations.
"""
from .models import Conversation,Notification,Message
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
        Marks all notifications related to conversations as seen.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: JSON response containing serialized conversation data.
        """
        user = request.user.id
        context = {"request": request}

        # Mark notifications as seen for the current user
        # Notification.objects.filter(user=request.user, is_seen=False).update(is_seen=True)

        # Retrieve conversations for the user
        conversations = Conversation.objects.filter(participants__id=user)
        
        conversation_serializer = SendConversationSerializer(conversations, context=context, many=True)
        return Response(conversation_serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieves a specific conversation between the authenticated user and another user.
        If the conversation does not exist, creates a new conversation.

        Args:
            request (Request): The HTTP request object.
            pk (str): The primary key of the user with whom the conversation is retrieved.

        Returns:
            Response: JSON response containing the conversation data and status.
        """
        try:
            receiver_id = pk
            sender_id = request.user.id

            # Fetch usernames
            sender_username = User.objects.get(pk=sender_id).username
            receiver_username = User.objects.get(pk=receiver_id).username

            # Construct conversation names
            sender_conv_name = f"{sender_username}_{receiver_username}"
            receiver_conv_name = f"{receiver_username}_{sender_username}"

            conversation = Conversation.objects.filter(
                Q(conversation_name=sender_conv_name, participants__id=pk)
                | Q(conversation_name=receiver_conv_name, participants__id=sender_id)
            ).first()

            if not conversation:
                conversation = Conversation.objects.create(conversation_name=receiver_conv_name)
                conversation.participants.add(sender_id, receiver_id)
                msg = "conversation created"
                status_code = status.HTTP_201_CREATED
            else:
                msg = "conversation already exists"
                status_code = status.HTTP_200_OK

            conversation_serializer = ConversationSerializer(conversation)
            
            return Response({
                "msg": msg,
                "conversation_name": conversation_serializer.data,
            }, status=status_code)

        except User.DoesNotExist:
            return Response({"msg": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"msg": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

