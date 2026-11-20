
from unittest.mock import Mock, patch

import requests

from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken


def make_access_token():
    token = AccessToken()
    token["user_id"] = "11111111-1111-1111-1111-111111111111"
    return str(token)


class IdentityLogoutProxyTests(APITestCase):

    def setUp(self):
        self.logout_url = "/api/identity/users/logout/"
        self.refresh_token = "example-refresh-token"
        self.access_token = make_access_token()

    @patch("gateway.views.forward_request")
    def test_logout_without_access_token(self, mock_forward):
        response = self.client.post(
            self.logout_url,
            {"refresh": self.refresh_token},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        mock_forward.assert_not_called()

    @patch("gateway.views.forward_request")
    def test_logout_with_valid_access_token(self, mock_forward):
        mock_response = Mock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.content = (
            b'{"success": true, "message": "Logout successful."}'
        )
        mock_response.headers = {
            "Content-Type": "application/json"
        }
        mock_forward.return_value = mock_response

        response = self.client.post(
            self.logout_url,
            {"refresh": self.refresh_token},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        mock_forward.assert_called_once()

        call_args = mock_forward.call_args.kwargs

        self.assertEqual(call_args["method"], "POST")
        self.assertEqual(
            call_args["url"],
            f"{settings.IDENTITY_SERVICE_URL}/api/users/logout/"
        )
        self.assertEqual(
            call_args["headers"]["Authorization"],
            f"Bearer {self.access_token}"
        )
        self.assertEqual(
            call_args["json"],
            {"refresh": self.refresh_token}
        )

    @patch("gateway.views.forward_request")
    def test_logout_propagates_identity_error(self, mock_forward):
        mock_response = Mock()
        mock_response.status_code = status.HTTP_401_UNAUTHORIZED
        mock_response.content = (
            b'{"success": false, "message": "Invalid refresh token."}'
        )
        mock_response.headers = {
            "Content-Type": "application/json"
        }
        mock_forward.return_value = mock_response

        response = self.client.post(
            self.logout_url,
            {"refresh": self.refresh_token},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        mock_forward.assert_called_once()

    @patch("gateway.views.forward_request")
    def test_logout_when_identity_service_is_unavailable(
        self,
        mock_forward
    ):
        mock_forward.side_effect = requests.RequestException()

        response = self.client.post(
            self.logout_url,
            {"refresh": self.refresh_token},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE
        )
        mock_forward.assert_called_once()
