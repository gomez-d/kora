
from datetime import timedelta
from unittest.mock import patch, Mock

from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


def make_access_token(expired=False):
    token = AccessToken()
    token["user_id"] = "11111111-1111-1111-1111-111111111111"

    if expired:
        token.set_exp(lifetime=timedelta(seconds=-1))

    return str(token)


def make_refresh_token():
    token = RefreshToken()
    token["user_id"] = "11111111-1111-1111-1111-111111111111"
    return str(token)


class JWTValidationTests(APITestCase):

    def setUp(self):
        self.mock_response = Mock()
        self.mock_response.status_code = 200
        self.mock_response.content = b'{"success": true}'
        self.mock_response.headers = {
            "Content-Type": "application/json"
        }

    @patch("gateway.views.forward_request")
    def test_login_without_token(self, mock_forward):
        mock_forward.return_value = self.mock_response

        response = self.client.post(
            "/api/identity/users/login/",
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_forward.assert_called_once()

    @patch("gateway.views.forward_request")
    def test_register_without_token(self, mock_forward):
        mock_forward.return_value = self.mock_response

        response = self.client.post(
            "/api/identity/users/register/",
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_forward.assert_called_once()

    def test_protected_route_without_token(self):
        response = self.client.get(
            "/api/business/foods/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            f"Respuesta recibida: {response.status_code} - {response.content.decode("utf-8", errors="replace")}"
        )

    @patch("gateway.views.forward_request")
    def test_protected_route_with_valid_token(self, mock_forward):
        mock_forward.return_value = self.mock_response
        token = make_access_token()

        response = self.client.get(
            "/api/business/foods/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_forward.assert_called_once()

    def test_expired_token(self):
        token = make_access_token(expired=True)

        response = self.client.get(
            "/api/business/foods/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            f"Respuesta recibida: {response.status_code} - {response.content.decode("utf-8", errors="replace")}"
        )

    def test_invalid_signature_token(self):
        token = make_access_token()
        parts = token.split(".")
        parts[2] = ("A" if parts[2][0] != "A" else "B") + parts[2][1:]
        invalid_token = ".".join(parts)

        response = self.client.get(
            "/api/business/foods/",
            HTTP_AUTHORIZATION=f"Bearer {invalid_token}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            f"Respuesta recibida: {response.status_code} - {response.content.decode("utf-8", errors="replace")}"
        )

    def test_refresh_token_rejected_as_access(self):
        token = make_refresh_token()

        response = self.client.get(
            "/api/business/foods/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            f"Respuesta recibida: {response.status_code} - {response.content.decode("utf-8", errors="replace")}"
        )
