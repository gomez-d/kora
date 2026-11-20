
from rest_framework.permissions import BasePermission


class HasBusinessPermission(BasePermission):
    """
    Allow access only when the authenticated identity contains
    the permission required by the requested business operation.
    """

    message = "You do not have permission to perform this operation."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        required_permissions = getattr(
            view,
            "required_permissions",
            {}
        )

        required_permission = required_permissions.get(request.method)

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
    permission and any supplied target user matches the authenticated user.
    """

    message = "You do not have permission to access this user's information."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        required_permissions = getattr(
            view,
            "required_permissions",
            {}
        )

        required_permission = required_permissions.get(request.method)

        if not required_permission:
            return False

        user_permissions = getattr(
            request.user,
            "permissions",
            []
        )

        if required_permission not in user_permissions:
            return False

        # The authenticated JWT is the source of the user's identity.
        authenticated_user_id = getattr(
            request.user,
            "user_id",
            None
        )

        if not authenticated_user_id:
            return False

        # user_id is optional because views obtain it from request.user.
        # If the client supplies one, it must match the authenticated user.
        if request.method in ("GET", "HEAD", "OPTIONS"):
            target_user_id = request.query_params.get("user_id")
        else:
            target_user_id = request.data.get("user_id")

        if target_user_id is not None:
            return str(target_user_id) == str(authenticated_user_id)

        return True


class HasOwnedBusinessPermission(BasePermission):
    """
    Allow access to an existing resource only when the authenticated
    identity has the required permission and owns the stored resource.
    """

    message = "You do not have permission to access this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        required_permissions = getattr(
            view,
            "required_permissions",
            {}
        )

        required_permission = required_permissions.get(request.method)

        if not required_permission:
            return False

        user_permissions = getattr(
            request.user,
            "permissions",
            []
        )

        return required_permission in user_permissions

    def has_object_permission(self, request, view, obj):
        resource_user_id = getattr(
            obj,
            "user_id",
            None
        )

        if resource_user_id is None:
            return False

        return str(resource_user_id) == str(request.user.user_id)
