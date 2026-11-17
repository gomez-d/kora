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

        # Obtain the permission required by the current HTTP method.
        required_permissions = getattr(
            view,
            "required_permissions",
            {}
        )

        required_permission = required_permissions.get(
            request.method
        )

        # Protected operations must explicitly declare a permission.
        if not required_permission:
            return False

        # Verify that the authenticated identity contains the required
        # permission provided by the trusted Identity service.
        user_permissions = getattr(
            request.user,
            "permissions",
            []
        )

        if required_permission not in user_permissions:
            return False

        # Ownership is checked using the trusted authenticated identity.
        # target_user_id = request.data.get("user_id")

        # Determine which user is the target of the request.
        # GET requests receive the target through query parameters,
        # while write operations receive it through the request body.
        if request.method == "GET":
            target_user_id = request.query_params.get("user_id")
        else:
            target_user_id = request.data.get("user_id")

        # Requests without a target user cannot pass the ownership check.
        if not target_user_id:
            return False

        # Compare the requested user with the trusted user_id extracted
        # from the validated JWT.
        return str(target_user_id) == str(request.user.user_id)

class HasOwnedBusinessPermission(BasePermission):
    """
    Allow access to an existing resource only when the authenticated
    identity has the required permission and owns the stored resource.
    """

    message = "You do not have permission to access this resource."

    def has_permission(self, request, view):
        # Authentication must be completed before evaluating authorization.
        if not request.user or not request.user.is_authenticated:
            return False

        # Obtain the permission required for the current HTTP method
        # from the protected view.
        required_permissions = getattr(
            view,
            "required_permissions",
            {}
        )

        required_permission = required_permissions.get(
            request.method
        )

        # Every protected operation must explicitly declare
        # the permission required to execute it.
        if not required_permission:
            return False

        # Read the effective permissions from the trusted identity
        # extracted from the validated JWT.
        user_permissions = getattr(
            request.user,
            "permissions",
            []
        )

        # The request may continue to the object lookup only when
        # the authenticated identity contains the required permission.
        return required_permission in user_permissions

    def has_object_permission(self, request, view, obj):
        # Obtain the owner stored in the resource itself.
        # This value comes from PostgreSQL and cannot be changed
        # by manipulating the request body or query parameters.
        resource_user_id = getattr(
            obj,
            "user_id",
            None
        )

        if resource_user_id is None:
            return False

        # Compare the persisted owner with the trusted user_id
        # extracted from the validated JWT.
        return str(resource_user_id) == str(request.user.user_id)