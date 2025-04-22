"""
URL configuration for conversation-related endpoints.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register the viewset with it
router = DefaultRouter()
router.register("conversation", views.ConversationView, basename="conversation")

urlpatterns = [
    path("", include(router.urls)),
]
