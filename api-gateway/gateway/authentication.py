
from uuid import UUID

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError


class GatewayAuthenticatedUser:
    """
    Represents an authenticated user in the API Gateway.
    """

    def __init__(self, user_id, roles=None, permissions=None):
        self.id = user_id
        self.user_id = user_id
        self.roles = roles or []
        self.permissions = permissions or []
        self.is_authenticated = True
        self.is_anonymous = False


class GatewayJWTAuthentication(BaseAuthentication):
    """
    Authenticate requests using access tokens issued by Identity.
    """

    keyword = "Bearer"

    def authenticate(self, request):
        authorization = request.headers.get("Authorization")

        if not authorization:
            return None

        parts = authorization.split()

        if len(parts) != 2 or parts[0].lower() != self.keyword.lower():
            raise AuthenticationFailed(
                "Invalid Authorization header format."
            )

        try:
            token = AccessToken(parts[1])
            payload = token.payload

        except TokenError as exc:
            raise AuthenticationFailed(
                "Invalid or expired access token."
            ) from exc

        if payload.get("token_type") != "access":
            raise AuthenticationFailed(
                "Access token required."
            )

        user_id = payload.get("user_id")

        if not isinstance(user_id, str) or not user_id.strip():
            raise AuthenticationFailed(
                "Token does not contain a valid user_id."
            )

        try:
            UUID(user_id)
        except ValueError as exc:
            raise AuthenticationFailed(
                "Invalid user_id format."
            ) from exc

        roles = payload.get("roles")
        permissions = payload.get("permissions")

        if not isinstance(roles, list):
            raise AuthenticationFailed("Invalid roles claim.")

        if not isinstance(permissions, list):
            raise AuthenticationFailed("Invalid permissions claim.")

        if not all(isinstance(role, str) for role in roles):
            raise AuthenticationFailed("Invalid roles claim.")

        if not all(
            isinstance(permission, str)
            for permission in permissions
        ):
            raise AuthenticationFailed("Invalid permissions claim.")

        request.jwt_payload = payload

        user = GatewayAuthenticatedUser(
            user_id=user_id,
            roles=roles,
            permissions=permissions,
        )

        return user, token

    def authenticate_header(self, request):
        return self.keyword
