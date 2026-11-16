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
            raise AuthenticationFailed(
                "Token has expired."
            )
        except InvalidTokenError:
            raise AuthenticationFailed(
                "Invalid token."
            )

        user_id = payload.get("user_id")
        roles = payload.get("roles", [])
        permissions = payload.get("permissions", [])

        if not user_id:
            raise AuthenticationFailed(
                "Token does not contain a valid user identity."
            )

        identity = AuthenticatedIdentity(
            user_id=str(user_id),
            roles=roles,
            permissions=permissions,
        )

        return identity, payload