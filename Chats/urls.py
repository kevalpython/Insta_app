from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("conversation", views.ConversationView, basename="conversation")


urlpatterns = [
        path("", include(router.urls)),

]
