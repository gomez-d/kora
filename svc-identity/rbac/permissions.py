from rest_framework.permissions import BasePermission


class IsKoraAdmin(BasePermission):
    """
    Allow access only to authenticated users with the ADMIN role.
    """

    message = "Administrator privileges are required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.roles.filter(
            name="ADMIN"
        ).exists()


class HasKoraPermission(BasePermission):
    """
    Allow access only when the authenticated user has the permission
    required by the requested operation through one of their roles.
    """

    message = "You do not have permission to perform this operation."

    def has_permission(self, request, view):
        # Authentication must exist before evaluating RBAC permissions.
        if not request.user or not request.user.is_authenticated:
            return False

        # Permissions may vary depending on the HTTP method.
        required_permissions = getattr(
            view,
            "required_permissions",
            {}
        )

        required_permission = required_permissions.get(
            request.method
        )

        # Protected views must explicitly declare the required permission.
        if not required_permission:
            return False

        # Verify the effective permission through:
        # User -> Role -> Permission.
        return request.user.roles.filter(
            permissions__name=required_permission
        ).exists()


class HasSelfOrKoraPermission(BasePermission):
    """
    Apply different permissions depending on whether the authenticated
    user is accessing their own resource or another user's resource.
    """

    message = "You do not have permission to access this resource."

    def has_permission(self, request, view):
        # Authentication must exist before evaluating RBAC permissions.
        if not request.user or not request.user.is_authenticated:
            return False

        target_user_id = view.kwargs.get("user_id")

        if target_user_id is None:
            return False

        is_own_resource = str(request.user.id) == str(target_user_id)

        if is_own_resource:
            permission_map = getattr(
                view,
                "self_permissions",
                {}
            )
        else:
            permission_map = getattr(
                view,
                "any_permissions",
                {}
            )

        required_permission = permission_map.get(
            request.method
        )

        if not required_permission:
            return False

        return request.user.roles.filter(
            permissions__name=required_permission
        ).exists()