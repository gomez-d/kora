
from unittest.mock import patch

import requests

from django.core.cache import cache

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken


def make_access_token(user_id="11111111-1111-1111-1111-111111111111"):
    token = AccessToken()
    token["user_id"] = user_id
    return str(token)


class ThrottleTests(APITestCase):

    def setUp(self):
        cache.clear()
        self.access_token = make_access_token()
        self.authorization = f"Bearer {self.access_token}"

    @patch(
        "gateway.views.forward_request",
        side_effect=requests.RequestException
    )
    def test_login_throttle_returns_429_after_limit(self, mock_forward):
        url = "/api/identity/users/login/"

        for _ in range(5):
            response = self.client.post(url, {}, format="json")
            self.assertNotEqual(
                response.status_code,
                status.HTTP_429_TOO_MANY_REQUESTS
            )

        response = self.client.post(url, {}, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS
        )
        self.assertEqual(mock_forward.call_count, 5)

    @patch(
        "gateway.views.forward_request",
        side_effect=requests.RequestException
    )
    def test_registration_throttle_returns_429_after_limit(
        self, mock_forward
    ):
        url = "/api/identity/users/register/"

        for _ in range(3):
            response = self.client.post(url, {}, format="json")
            self.assertNotEqual(
                response.status_code,
                status.HTTP_429_TOO_MANY_REQUESTS
            )

        response = self.client.post(url, {}, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS
        )
        self.assertEqual(mock_forward.call_count, 3)

    @patch(
        "gateway.views.forward_request",
        side_effect=requests.RequestException
    )
    def test_refresh_throttle_returns_429_after_limit(
        self, mock_forward
    ):
        url = "/api/identity/users/token/refresh/"

        for _ in range(10):
            response = self.client.post(url, {}, format="json")
            self.assertNotEqual(
                response.status_code,
                status.HTTP_429_TOO_MANY_REQUESTS
            )

        response = self.client.post(url, {}, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS
        )
        self.assertEqual(mock_forward.call_count, 10)

    @patch(
        "gateway.views.forward_request",
        side_effect=requests.RequestException
    )
    def test_business_throttle_returns_429_after_limit(
        self, mock_forward
    ):
        url = "/api/business/test/"

        for _ in range(60):
            response = self.client.get(
                url,
                HTTP_AUTHORIZATION=self.authorization
            )
            self.assertNotEqual(
                response.status_code,
                status.HTTP_429_TOO_MANY_REQUESTS
            )

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS
        )
        self.assertEqual(mock_forward.call_count, 60)

    @patch(
        "gateway.views.forward_request",
        side_effect=requests.RequestException
    )
    def test_ai_throttle_returns_429_after_limit(
        self, mock_forward
    ):
        url = "/api/ai/test/"

        for _ in range(60):
            response = self.client.post(
                url,
                {},
                format="json",
                HTTP_AUTHORIZATION=self.authorization
            )
            self.assertNotEqual(
                response.status_code,
                status.HTTP_429_TOO_MANY_REQUESTS
            )

        response = self.client.post(
            url,
            {},
            format="json",
            HTTP_AUTHORIZATION=self.authorization
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS
        )
        self.assertEqual(mock_forward.call_count, 60)
