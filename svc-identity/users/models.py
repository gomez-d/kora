import uuid
import hashlib
import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields["is_staff"]:
            raise ValueError("Superuser must have is_staff=True")

        if not extra_fields["is_superuser"]:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


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
    username = None
    email = models.EmailField(
        unique=True
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True
    )
    roles = models.ManyToManyField(
        "rbac.Role",
        through="rbac.UserRole",
        related_name="users",
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )
    token_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
    )
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @staticmethod
    def hash_token(token):
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

    @classmethod
    def create_for_user(cls, user, expiration_minutes=30):
        cls.objects.filter(
            user=user,
            used=False,
        ).update(used=True)

        raw_token = secrets.token_urlsafe(32)

        cls.objects.create(
            user=user,
            token_hash=cls.hash_token(raw_token),
            expires_at=(
                timezone.now() + timedelta(minutes=expiration_minutes)
            ),
        )

        return raw_token

    def is_valid(self):
        return (
            not self.used
            and self.expires_at > timezone.now()
        )

    def consume(self):
        if not self.is_valid():
            return False

        self.used = True
        self.save(update_fields=["used"])

        return True

    @classmethod
    def get_valid_token(cls, raw_token):
        token_hash = cls.hash_token(raw_token)

        try:
            token = cls.objects.get(
                token_hash=token_hash,
            )
        except cls.DoesNotExist:
            return None

        if not token.is_valid():
            return None

        return token