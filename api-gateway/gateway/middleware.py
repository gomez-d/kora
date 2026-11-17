from django.http import JsonResponse
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError


PUBLIC_PATHS = {
    "/api/health",
    "/api/identity/users/health",
    "/api/identity/users/register",
    "/api/identity/users/login",
    "/api/identity/users/token/refresh",
    "/api/business/health",
}


class GatewayJWTMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        path = request.path.rstrip("/")

        protected_prefixes = (
            "/api/identity/",
            "/api/business/",
            "/api/ai/",
        )

        is_protected_route = path.startswith(
            protected_prefixes
        )

        if not is_protected_route:
            return self.get_response(request)

        if path in PUBLIC_PATHS:
            return self.get_response(request)

        authorization = request.headers.get(
            "Authorization", ""
        )

        parts = authorization.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JsonResponse(
                {
                    "success": False,
                    "message": "Authentication credentials were not provided."
                },
                status=401
            )

        try:
            token = AccessToken(parts[1])
            request.jwt_payload = token.payload

        except TokenError:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid or expired access token."
                },
                status=401
            )

        return self.get_response(request)