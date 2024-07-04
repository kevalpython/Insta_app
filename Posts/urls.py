from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("addpost", views.AddPostView, basename="addpost")


urlpatterns = [
    path("", include(router.urls)),
]
