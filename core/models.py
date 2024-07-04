from django.db import models

class BaseModel(models.Model):
    """
    Abstract base model with common fields for other models.
    """

    class Meta:
        """
        Metadata options for the CommentSerializer.
        """

        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)