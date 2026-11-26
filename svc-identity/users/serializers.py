from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings

from clients.unstructured_data_client import send_identity_event

from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError

from users.models import User

from rbac.models import Role, UserRole
from rbac.utils import (
    get_user_role_names,
    get_user_permission_names
)

class StrictFieldsMixin:
    """
    Reject input fields that are not part of the serializer contract.
    """

    def to_internal_value(self, data):
        if hasattr(data, "keys"):
            unexpected_fields = set(data.keys()) - set(self.fields.keys())

            if unexpected_fields:
                raise serializers.ValidationError({
                    "unexpected_fields": (
                        "Unexpected field(s): "
                        f"{', '.join(sorted(unexpected_fields))}."
                    )
                })
        return super().to_internal_value(data)

class UserRegistrationSerializer(StrictFieldsMixin, serializers.ModelSerializer):
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

    def validate_first_name(self, value):
        """
        Reject empty or whitespace-only first names.
        """

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "First name cannot be empty."
            )

        return value

    def validate_last_name(self, value):
        """
        Reject empty or whitespace-only last names.
        """

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Last name cannot be empty."
            )

        return value

    def validate_password(self, value):
        user = User(
            email=self.initial_data.get("email", ""),
            first_name=self.initial_data.get("first_name", ""),
            last_name=self.initial_data.get("last_name", "")
        )

        validate_password(value, user=user)

        return value

    def validate_date_of_birth(self, value):
        """
        Validate that the date produces an age between 1 and 120 years.
        """

        today = timezone.localdate()

        if value > today:
            raise serializers.ValidationError(
                "Date of birth cannot be in the future."
            )

        age = today.year - value.year

        if(today.month, today.day) < (value.month, value.day):
            age -= 1

        if age < 1 or age > 120:
            raise serializers.ValidationError(
                "Age must be between 1 and 120 years."
            )

        return value

    def validate_email(self, value):
        """
        Normalize the email before persistence.
        """

        return value.strip().lower()

    def create(self, validated_data):
        """
        Create the user and notify the unstructured data service
        about the registration event.
        """

        # Create the user in the identity database.
        user = User.objects.create_user(**validated_data)

        # Get the default role assigned to standard Kora users.
        default_role = Role.objects.get(name="USER")

        # Associate the default role with the new user.
        UserRole.objects.create(
            user=user,
            role=default_role
        )

        # Send the registration event to the unstructured data service.
        send_identity_event(
            user_id=user.id,
            event='user_registered',
            level='INFO',
            metadata={
                "source": "user_registration",
            },
        )

        return user

    def validate(self, attrs):
        """
        Prevent clients from assigning roles during registration.
        """

        if "role" in self.initial_data or "roles" in self.initial_data:
            raise serializers.ValidationError(
                {
                    "role": [
                        "Role assignment is not allowed during registration."
                    ]
                }
            )

        return attrs


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


class UserUpdateSerializer(StrictFieldsMixin, serializers.ModelSerializer):
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

    def validate_first_name(self, value):
        """
        Reject empty whitespace-only first names.
        """

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "First name cannot be empty."
            )

        return value

    def validate_last_name(self, value):
        """
        Reject empty or whitespace-only last names.
        """

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Last name cannot be empty."
            )

        return value

    def validate_date_of_birth(self, value):
        """
        Validate that the date produces an age between 1 and 120 years.
        """

        today = timezone.localdate()

        if value > today:
            raise serializers.ValidationError(
                "Date of birth cannot be in the future."
            )

        age = today.year - value.year

        if(today.month, today.day) < (value.month, value.day):
            age -= 1

        if age < 1 or age > 120:
            raise serializers.ValidationError(
                "Age must be between 1 and 120 years."
            )

        return value

    def validate_email(self, value):
        """
        Normalize the email before persistence.
        """

        return value.strip().lower()


class UserLoginSerializer(StrictFieldsMixin, serializers.Serializer):
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

    def validate_email(self, value):
        """
        Normalize the email before authentication.
        """

        return value.strip().lower()

class UserTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Refresh the access token using the user's current roles.

    Role information is always retrieved from the identity database
    and is never accepted from the client.
    """

    def validate(self, attrs):
        # Validate and decode the refresh token.
        refresh = self.token_class(attrs["refresh"])

        # Retrieve the user identifier from the signed token.
        user_id = refresh.get(api_settings.USER_ID_CLAIM)

        try:
            # Retrieve the current active user from the identity database.
            user = User.objects.get(
                id=user_id,
                is_active=True
            )
        except User.DoesNotExist:
            raise AuthenticationFailed(
                "User not found or inactive."
            )

        # Recalculate the role context using the current database state.
        refresh["roles"] = get_user_role_names(user)

        # Recalculate the current effective permissions.
        refresh["permissions"] = get_user_permission_names(user)

        # Pass the updated signed refresh token to SimpleJWT.
        attrs["refresh"] = str(refresh)

        return super().validate(attrs)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(
        write_only=True
    )
    new_password = serializers.CharField(
        write_only=True
    )

    def validate_new_password(self, value):
        # Reuse Django's configured password validators to enforce
        # the same security policy used throughout the Identity service.
        try:
            validate_password(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                list(error.messages)
            )

        return value