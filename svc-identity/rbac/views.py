from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from users.models import User

from rbac.models import (
    Role,
    Permission,
    UserRole,
    RolePermission
)

from rbac.serializers import (
    RoleReadSerializer,
    RoleWriteSerializer,
    PermissionReadSerializer,
    PermissionWriteSerializer,
    UserRoleReadSerializer,
    UserRoleWriteSerializer,
    RolePermissionReadSerializer,
    RolePermissionWriteSerializer,
    UserRolesQuerySerializer
)


class RoleView(APIView):
    def get(self, request):
        roles = Role.objects.all()

        serializer = RoleReadSerializer(roles, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = RoleWriteSerializer(data=request.data)

        if serializer.is_valid():
            role = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Role created successfully.",
                    "data": RoleReadSerializer(role).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "message": "Validation error.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class RoleDetailView(APIView):
    def get_object(self, role_id):
        try:
            return Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return None

    def get(self, request, role_id):
        role = self.get_object(role_id)

        if role is None:
            return Response(
                {
                    "success": False,
                    "message": "Role not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RoleReadSerializer(role)

        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def put(self, request, role_id):
        return self.update_role(request, role_id)

    def patch(self, request, role_id):
        return self.update_role(request, role_id, partial=True)

    def update_role(self, request, role_id, partial=False):
        role = self.get_object(role_id)

        if role is None:
            return Response(
                {
                    "success": False,
                    "message": "Role not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RoleWriteSerializer(
            role,
            data=request.data,
            partial=partial
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Role updated successfully.",
                    "data": RoleReadSerializer(role).data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "message": "Validation error.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, role_id):
        role = self.get_object(role_id)

        if role is None:
            return Response(
                {
                    "success": False,
                    "message": "Role not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        role.delete()

        return Response(
            {
                "success": True,
                "message": "Role deleted successfully."
            },
            status=status.HTTP_200_OK
        )


class PermissionView(APIView):
    def get(self, request):
        permissions = Permission.objects.all()

        serializer = PermissionReadSerializer(permissions, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = PermissionWriteSerializer(data=request.data)

        if serializer.is_valid():
            permission = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Permission created successfully.",
                    "data": PermissionReadSerializer(permission).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "message": "Validation error.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class PermissionDetailView(APIView):
    def get_object(self, permission_id):
        try:
            return Permission.objects.get(id=permission_id)
        except Permission.DoesNotExist:
            return None

    def get(self, request, permission_id):
        permission = self.get_object(permission_id)

        if permission is None:
            return Response(
                {
                    "success": False,
                    "message": "Permission not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PermissionReadSerializer(permission)

        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def put(self, request, permission_id):
        return self.update_permission(request, permission_id)

    def patch(self, request, permission_id):
        return self.update_permission(request, permission_id, partial=True)

    def update_permission(self, request, permission_id, partial=False):
        permission = self.get_object(permission_id)

        if permission is None:
            return Response(
                {
                    "success": False,
                    "message": "Permission not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PermissionWriteSerializer(
            permission,
            data=request.data,
            partial=partial
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Permission updated successfully.",
                    "data": PermissionReadSerializer(permission).data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "message": "Validation error.",
                "errors": serializer.errors
            }
        )

    def delete(self, request, permission_id):
        permission = self.get_object(permission_id)

        if permission is None:
            return Response(
                {
                    "success": False,
                    "message": "Permission not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        permission.delete()

        return Response(
            {
                "success": True,
                "message": "Permission deleted successfully."
            }
        )


class UserRoleView(APIView):
    def get(self, request):
        user_roles = UserRole.objects.all()

        serializer = UserRoleReadSerializer(user_roles, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = UserRoleWriteSerializer(data=request.data)

        if serializer.is_valid():
            user_role = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Role assigned to user successfully.",
                    "data": UserRoleReadSerializer(user_role).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "message": "Validation error.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class UserRoleDetailView(APIView):
    def get_object(self, user_role_id):
        try:
            return UserRole.objects.get(id=user_role_id)
        except UserRole.DoesNotExist:
            return None

    def get(self, request, user_role_id):
        user_role = self.get_object(user_role_id)

        if user_role is None:
            return Response(
                {
                    "success": False,
                    "message": "User role assigment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserRoleReadSerializer(user_role)

        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def delete(self, request, user_role_id):
        user_role = self.get_object(user_role_id)

        if user_role is None:
            return Response(
                {
                    "success": False,
                    "message": "User role assigment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        user_role.delete()

        return Response(
            {
                "success": True,
                "message": "Role unassigned from user successfully"
            },
            status=status.HTTP_200_OK
        )


class RolePermissionView(APIView):
    def get(self, request):
        role_permissions = RolePermission.objects.all()

        serializer = RolePermissionReadSerializer(role_permissions, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = RolePermissionWriteSerializer(data=request.data)

        if serializer.is_valid():
            role_permission = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Permission assigned to role successfully.",
                    "data": RolePermissionReadSerializer(role_permission).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "message": "Validation error.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class RolePermissionDetailView(APIView):
    def get_object(self, role_permission_id):
        try:
            return RolePermission.objects.get(id=role_permission_id)
        except RolePermission.DoesNotExist:
            return None

    def get(self, request, role_permission_id):
        role_permission = self.get_object(role_permission_id)

        if role_permission is None:
            return Response(
                {
                    "success": False,
                    "message": "Role permission assigment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RolePermissionReadSerializer(role_permission)

        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def delete(self, request, role_permission_id):
        role_permission = self.get_object(role_permission_id)

        if role_permission is None:
            return Response(
                {
                    "success": False,
                    "message": "Role permission assigment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        role_permission.delete()

        return Response(
            {
                "success": True,
                "message": "Permission unassigned from role successfully."
            },
            status=status.HTTP_200_OK
        )

class UserRolesQueryView(APIView):
    """
    Allow authorized users to retrieve the roles assigned to a user.

    Standard users may only retrieve their own roles.
    Administrators may retrieve roles assigned to other users.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        # Retrieve only active users.
        try:
            user = User.objects.get(
                id=user_id,
                is_active=True
            )
        except User.DoesNotExist:
            return Response(
                {
                    "detail": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Standard users may only consult their own roles.
        is_own_user = request.user.id == user.id

        # Administrators may consult roles assigned to other users.
        is_admin = request.user.roles.filter(
            name="ADMIN"
        ).exists()

        if not is_own_user and not is_admin:
            return Response(
                {
                    "detail": "You are not authorized to view this user's roles."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        data = {
            "user_id": user.id,
            "roles": list(
                user.roles.values_list(
                    "name",
                    flat=True
                )
            )
        }

        serializer = UserRolesQuerySerializer(data)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )