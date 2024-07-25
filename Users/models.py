from django.db import models
from django.contrib.auth.models import AbstractUser


def upload_to(instance, filename):
    return f"images/{instance.username}/Profile/{filename}"


class User(AbstractUser):
    """
    Custom user model with additional fields.
    """

    profile_img = models.ImageField(upload_to=upload_to, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        """
        String representation of a user.
        """
        return str(self.username)
