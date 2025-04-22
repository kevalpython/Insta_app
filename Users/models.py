"""
Models for defining custom user model and associated fields.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser

def upload_to(instance, filename):
    """
    Function to define the upload path for user profile images.

    Args:
        instance (User): Instance of the User model.
        filename (str): Original filename of the uploaded file.

    Returns:
        str: Path to upload the file, formatted as "images/{username}/Profile/{filename}".
    """
    return f"images/{instance.username}/Profile/{filename}"

class User(AbstractUser):
    """
    Custom user model with additional fields.

    Attributes:
        profile_img (ImageField): Field for storing user's profile image.
        created_at (DateTimeField): Field for storing the timestamp when the user account was created.
        updated_at (DateTimeField): Field for storing the timestamp when the user account was last updated.

    Methods:
        __str__: Returns the string representation of the user instance.
    """

    profile_img = models.ImageField(upload_to=upload_to, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        """
        String representation of a user.

        Returns:
            str: Username of the user instance.
        """
        return str(self.username)
