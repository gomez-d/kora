from rest_framework.permissions import BasePermission


PUBLIC_PATHS = {
    "/api/identity/users/register/",
    "/api/identity/users/login/",
    "/api/identity/users/token/refresh/",
}

PUBLIC_PATH_PREFIXES = (
    "/api/health/",
    "/api/schema/",
)


class IsAuthenticatedOrPublicRoute(BasePermission):

    def has_permission(self, request, view):
        path = request.path

        if path in PUBLIC_PATHS:
            return True

        if any(path.startswith(prefix) for prefix in PUBLIC_PATH_PREFIXES):
            return True

        return bool(getattr(request.user, "is_authenticated", False))