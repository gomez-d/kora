from rest_framework import serializers
from rbac.models import (
    Role,
    Permission,
    UserRole,
    RolePermission
)


class RoleReadSerializer(serializers.ModelSerializer):
    permissions = serializers.StringRelatedField(many=True)

    class Meta:
        model = Role

        fields = [
            "id",
            "name",
            "description",
            "permissions"
        ]

        read_only_fields = fields


class RoleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            "name",
            "description"
        ]


class PermissionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission

        fields = [
            "id",
            "name",
            "resource",
            "action",
            "description"
        ]

        read_only_fields = fields


class PermissionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission

        fields = [
            "name",
            "resource",
            "action",
            "description"
        ]


class UserRoleReadSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    role = serializers.StringRelatedField()

    class Meta:
        model = UserRole

        fields = [
            "id",
            "user",
            "role"
        ]

        read_only_fields = fields


class UserRoleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole

        fields = [
            "user",
            "role"
        ]


class RolePermissionReadSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()
    permission = serializers.StringRelatedField()

    class Meta:
        model = RolePermission

        fields = [
            "id",
            "role",
            "permission"
        ]

        read_only_fields = fields


class RolePermissionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission

        fields = [
            "role",
            "permission"
        ]
