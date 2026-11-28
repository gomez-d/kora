import jwt

from django.conf import settings


def generate_test_token(
    user_id,
    roles=None,
    permissions=None,
):
    """
    Generate a signed JWT for Business API tests.
    """

    payload = {
        "user_id": str(user_id),
        "token_type": "access",
        "roles": roles or ["USER"],
        "permissions": permissions or [],
    }

    return jwt.encode(
        payload,
        settings.JWT_SIGNING_KEY,
        algorithm="HS256",
    )


def authenticate_test_client(
    client,
    user_id,
    roles=None,
    permissions=None,
):
    """
    Authenticate an API test client using a Bearer token.
    """

    token = generate_test_token(
        user_id=user_id,
        roles=roles,
        permissions=permissions,
    )

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {token}"
    )
