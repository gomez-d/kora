
from dataclasses import dataclass

from django.conf import settings
from jwt import ExpiredSignatureError, InvalidTokenError, decode
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


@dataclass
class AuthenticatedIdentity:
    """
    Represent the trusted identity extracted from a validated JWT.
    """

    user_id: str
    roles: list
    permissions: list

    @property
    def is_authenticated(self):
        return True


class KoraJWTAuthentication(BaseAuthentication):
    """
    Authenticate requests using JWTs issued by the Identity service.
    """

    keyword = "Bearer"

    def authenticate(self, request):
        authorization = request.headers.get("Authorization")

        if not authorization:
            return None

        parts = authorization.split()

        if len(parts) != 2 or parts[0] != self.keyword:
            raise AuthenticationFailed(
                "Invalid authorization header."
            )

        token = parts[1]

        try:
            payload = decode(
                token,
                settings.JWT_SIGNING_KEY,
                algorithms=["HS256"],
            )
        except ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.")
        except InvalidTokenError:
            raise AuthenticationFailed("Invalid token.")

        user_id = payload.get("user_id")
        token_type = payload.get("token_type")
        roles = payload.get("roles")
        permissions = payload.get("permissions")

        if token_type != "access":
            raise AuthenticationFailed(
                "Only access tokens are accepted."
            )

        if not isinstance(user_id, str) or not user_id.strip():
            raise AuthenticationFailed(
                "Token does not contain a valid user identity."
            )

        if not isinstance(roles, list) or not all(
            isinstance(role, str) for role in roles
        ):
            raise AuthenticationFailed(
                "Invalid roles claim."
            )

        if not isinstance(permissions, list) or not all(
            isinstance(permission, str) for permission in permissions
        ):
            raise AuthenticationFailed(
                "Invalid permissions claim."
            )

        identity = AuthenticatedIdentity(
            user_id=user_id,
            roles=roles,
            permissions=permissions,
        )

        return identity, payload

    def authenticate_header(self, request):
        return self.keyword
