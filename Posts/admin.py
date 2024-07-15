from django.contrib import admin
from .models import Post,PostImageVideo,Like,Comment,Friendship


# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    This class displays user data in the admin panel.
    """

    list_display = ["id", "user", "content"]


@admin.register(PostImageVideo)
class PostImageVideoAdmin(admin.ModelAdmin):
    """
    This class displays user data in the admin panel.
    """

    list_display = ["id", "post"]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """
    This class displays user data in the admin panel.
    """

    list_display = ["id", "user", "post","is_like"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    This class displays user data in the admin panel.
    """

    list_display = ["id", "user", "post", "content"]


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    """
    This class displays user data in the admin panel.
    """

    list_display = ["id", "from_user", "to_user", "is_accepted"]
