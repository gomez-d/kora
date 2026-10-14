from rest_framework import serializers
from users.models import User
from clients.unstructured_data_client import send_identity_event

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer used to register Kora users.

    user_id exposes the UUID primary key used to identify the user
    across Kora microservices.
    """

    user_id = serializers.UUIDField(
        source='id',
        read_only=True
    )

    password = serializers.CharField(
        write_only = True,
        required = True
    )

    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name'
        ]
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

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
                'username': user.username
            },
            metadata={
                'source': 'user_registration',
            },
        )

        return user

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )

        return value