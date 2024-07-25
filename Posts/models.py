from django.db import models
from Users.models import User
from core.models import BaseModel


class Post(BaseModel):
    """
        Post model creating a Posts for user.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        """
            String method to display object in string.
        """
        return f"Post by {self.user.username} at {self.created_at}"


def upload_post_file(instance, filename):
    return f"images/posts/images/{filename}"


class PostImageVideo(BaseModel):
    """
        Post Image/Video model to keep multiple file.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_post_file, blank=True, null=True)


class Like(BaseModel):
    """
        Likes model for Post.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    is_like = models.BooleanField(default=False)


class Comment(BaseModel):
    """
        Comments model for Post.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"


class Friendship(BaseModel):
    """
        Friendship model for making friendship with multiple user for Post.
    """
    from_user = models.ForeignKey(
        User, related_name="friendships_created", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        User, related_name="friendships_received", on_delete=models.CASCADE
    )
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.from_user} follows {self.to_user}"
