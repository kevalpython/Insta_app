from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("addpost", views.AddPostView, basename="addpost")
router.register("post", views.PostView, basename="post")
router.register("deletepost", views.DeletePostView, basename="deletepost")
router.register("likepost", views.LikePostView, basename="likepost")
router.register("addcommentpost", views.AddCommentView, basename="addcommentpost")
router.register("friendrequestsend", views.FriendRequestSendView, basename="friendrequestsend")
router.register("friendrequestaccepted", views.FriendRequestAcceptView, basename="friendrequestaccepted")
router.register("unfollowfriendrequest", views.UnfollowFriendRequestView, basename="unfollowfriendrequest")

urlpatterns = [
    path("", include(router.urls)),
]
