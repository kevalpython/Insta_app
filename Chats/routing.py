"""
WebSocket routing configuration for chat application.
"""
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<str:conversation_name>/', consumers.ChatConsumer.as_asgi()),
    path('ws/notification/<str:username>/', consumers.NotificationConsumer.as_asgi()),
]
