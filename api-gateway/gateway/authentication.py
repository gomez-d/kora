
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class GatewayAuthenticatedUser:
    def __init__(self, user_id):
        self.id = user_id
        self.is_authenticated = True
        self.is_anonymous = False


class GatewayJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationFailed("Invalid Authorization header format.")

        raw_token = parts[1]

        try:
            token = AccessToken(raw_token)

            if token.get("token_type") != "access":
                raise AuthenticationFailed("Access token required.")

        except (InvalidToken, TokenError) as exc:
            raise AuthenticationFailed("Invalid or expired token.") from exc

        request.jwt_payload = token.payload

        user_id = token.payload.get("user_id")

        if not user_id:
            raise AuthenticationFailed("Token does not contain user_id.")

        user = GatewayAuthenticatedUser(user_id)

        return (user, token)

    def authenticate_header(self, request):
        return "Bearer"
