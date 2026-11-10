from rest_framework import serializers
from clients.unstructured_data_client import send_identity_event
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from users.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer used to register Kora users.

    user_id exposes the UUID primary key used to identify the user
    across Kora microservices.
    """

    user_id = serializers.UUIDField(
        source="id",
        read_only=True
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        trim_whitespace=False
    )

    class Meta:
        model = User

        fields = [
            "user_id",
            "email",
            "password",
            "first_name",
            "last_name",
            "date_of_birth",
        ]

        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "date_of_birth": {
                "required": True,
                "allow_null": False
            }
        }

    def validate_password(self, value):
        user = User(
            email=self.initial_data.get("email", ""),
            first_name=self.initial_data.get("first_name", ""),
            last_name=self.initial_data.get("last_name", "")
        )

        validate_password(value, user=user)

        return value

    def validate_date_of_birth(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError(
                "Date of birth cannot be in the future."
            )

        return value

    def create(self, validated_data):
        """
        Create the user and notify the unstructured data service
        about the registration event.
        """

        # Create the user in the identity database.
        user = User.objects.create_user(**validated_data)

        # Send the registration event to the unstructured data service.
        send_identity_event(
            user_id=user.id,
            event='user_registered',
            data={
                "email": user.email
            },
            metadata={
                "source": "user_registration",
            },
        )

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer used to retrieve user information.
    """

    user_id = serializers.UUIDField(
        source="id",
        read_only=True
    )

    class Meta:
        model = User

        fields = [
            "user_id",
            "email",
            "first_name",
            "last_name",
            "date_of_birth"
        ]

        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer used to update user information.
    """

    class Meta:
        model = User

        fields = [
            "email",
            "first_name",
            "last_name",
            "date_of_birth"
        ]

    def validate_date_of_birth(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError(
                "Date of birth cannot be in the future."
            )

        return value


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer used to validate login credentials.
    """

    email = serializers.EmailField(
        required=True,
        allow_blank=False
    )
    password = serializers.CharField(
        required=True,
        allow_blank=False,
        write_only=True,
        trim_whitespace=False
    )
