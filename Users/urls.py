from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

router = DefaultRouter()
router.register("register", views.RegisterView, basename="register")
router.register("userprofile", views.UserProfileView, basename="userprofile")
router.register("searchuser", views.SearchUserView, basename="searchuser")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="verify"),
    path("logout/",views.LogoutView.as_view(), name="logout"),
]