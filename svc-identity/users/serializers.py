from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from clients.unstructured_data_client import send_identity_event
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from users.models import User

from rbac.models import Role, UserRole
from rbac.utils import get_user_role_names


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
            data={
                "email": user.email
            },
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

        # Pass the updated signed refresh token to SimpleJWT.
        attrs["refresh"] = str(refresh)

        return super().validate(attrs)