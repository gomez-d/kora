from rest_framework import serializers
from users.models import User

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
        return User.objects.create_user(**validated_data)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )

        return value