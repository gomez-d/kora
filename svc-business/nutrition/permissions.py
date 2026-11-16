from rest_framework.permissions import BasePermission


class HasBusinessPermission(BasePermission):
    """
    Allow access only when the authenticated identity contains
    the permission required by the requested business operation.
    """

    message = "You do not have permission to perform this operation."

    def has_permission(self, request, view):
        # Authentication must be completed first.
        if not request.user or not request.user.is_authenticated:
            return False

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

        user_permissions = getattr(
            request.user,
            "permissions",
            []
        )

        return required_permission in user_permissions

class HasSelfBusinessPermission(BasePermission):
    """
    Allow access only when the authenticated identity has the required
    self-scoped permission and the target user matches the authenticated user.
    """

    message = "You do not have permission to access this user's information."

    def has_permission(self, request, view):
        # Authentication must be completed first.
        if not request.user or not request.user.is_authenticated:
            return False

        required_permissions = getattr(
            view,
            "required_permissions",
            {}
        )

        required_permission = required_permissions.get(
            request.method
        )

        if not required_permission:
            return False

        user_permissions = getattr(
            request.user,
            "permissions",
            []
        )

        if required_permission not in user_permissions:
            return False

        # Ownership is checked using the trusted authenticated identity.
        target_user_id = request.data.get("user_id")

        if request.method == "GET":
            target_user_id = request.query_params.get("user_id")

        if not target_user_id:
            return False

        return str(target_user_id) == str(request.user.user_id)