import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom Kora user model.

    The primary key uses UUID so the same identifier can be shared 
    across Kora microservices.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )