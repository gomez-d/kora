from rest_framework.permissions import BasePermission


class IsKoraAdmin(BasePermission):
    """
    Allow access only to authenticated users with the ADMIN role.
    """

    message = "Administrator privileges are required."

    def has_permission(self, request, view):
        # Reject unauthenticated requests.
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow only users assigned to the ADMIN role.
        return request.user.roles.filter(
            name="ADMIN"
        ).exists()