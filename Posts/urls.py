from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("addpost", views.AddPostView, basename="addpost")
router.register("postlist", views.PostListView, basename="postlist")
router.register("userpost", views.UserPostView, basename="userpost")
router.register("deletepost", views.DeletePostView, basename="deletepost")
router.register("likepost", views.LikePostView, basename="likepost")
router.register("addcommentpost", views.AddCommentView, basename="addcommentpost")
router.register("friendrequestsend", views.FriendRequestSendView, basename="friendrequestsend")
router.register("friendrequestaccepted", views.FriendRequestAcceptView, basename="friendrequestaccepted")
router.register("unfollowfriendrequest", views.UnfollowFriendRequestView, basename="unfollowfriendrequest")
router.register("rejectfriendrequest", views.RejectFriendRequestView, basename="rejectfriendrequest")
router.register("sendfollowbackrequest", views.FollowBackFriendRequestsendView, basename="sendfollowbackrequest")
router.register("acceptfollowbackrequest", views.FollowBackRequestAcceptedView, basename="acceptfollowbackrequest")
router.register("acceptfollowrequest", views.FollowRequestAccepted, basename="acceptfollowrequest")
router.register("friendslist", views.FriendsListView, basename="friendslist")

urlpatterns = [
    path("", include(router.urls)),
]
