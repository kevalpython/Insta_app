from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("userpost", views.UserPostView, basename="userpost")
router.register("likepost", views.LikePostView, basename="likepost")
router.register("addcommentpost", views.AddCommentView, basename="addcommentpost")
router.register("friendship", views.FriendRequestSendView, basename="friendship")

urlpatterns = [
    path("", include(router.urls)),
]
