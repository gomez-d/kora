
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from users.models import User


class UserLogoutTests(APITestCase):
    """
    Tests for user logout and refresh token revocation.
    """

    def setUp(self):
        self.logout_url = reverse("user-logout")

        self.user = User.objects.create_user(
            email="logout@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="Logout",
        )

        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.refresh)
        self.access_token = str(self.refresh.access_token)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

    def logout_request(self, token):
        return self.client.post(
            self.logout_url,
            {"refresh": token},
            format="json",
        )

    def test_logout_with_valid_refresh_token(self):
        response = self.logout_request(self.refresh_token)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(response.data["success"])

    def test_logout_blacklists_refresh_token(self):
        response = self.logout_request(self.refresh_token)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        outstanding = OutstandingToken.objects.get(
            token=self.refresh_token
        )

        self.assertTrue(
            BlacklistedToken.objects.filter(
                token=outstanding
            ).exists()
        )

    def test_logout_without_authentication_is_rejected(self):
        self.client.credentials()

        response = self.logout_request(self.refresh_token)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_without_refresh_token_is_rejected(self):
        response = self.client.post(
            self.logout_url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_logout_with_invalid_refresh_token_is_rejected(self):
        response = self.logout_request(
            "invalid-refresh-token"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_with_another_users_refresh_token_is_rejected(self):
        another_user = User.objects.create_user(
            email="another@example.com",
            password="TestPassword123!",
        )

        another_refresh = RefreshToken.for_user(another_user)

        response = self.logout_request(str(another_refresh))

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_with_already_revoked_token_is_rejected(self):
        self.logout_request(self.refresh_token)

        response = self.logout_request(self.refresh_token)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
