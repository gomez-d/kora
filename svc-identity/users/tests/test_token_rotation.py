
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
)

from users.models import User


class TokenRotationTests(APITestCase):
    """
    Tests for refresh token rotation and invalidation.
    """

    def setUp(self):
        self.refresh_url = reverse("token-refresh")

        self.user = User.objects.create_user(
            email="rotation@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="Rotation",
        )

        self.refresh_token = str(
            RefreshToken.for_user(self.user)
        )

    def refresh_request(self, token):
        return self.client.post(
            self.refresh_url,
            {"refresh": token},
            format="json",
        )

    def test_refresh_with_valid_token_returns_new_tokens(self):
        response = self.refresh_request(self.refresh_token)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_generates_new_access_token(self):
        response = self.refresh_request(self.refresh_token)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertNotEqual(
            response.data["access"],
            "",
        )

    def test_refresh_generates_new_refresh_token(self):
        response = self.refresh_request(self.refresh_token)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertNotEqual(
            response.data["refresh"],
            self.refresh_token,
        )


    def test_old_refresh_token_is_rejected_after_rotation(self):
        response = self.refresh_request(self.refresh_token)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        from rest_framework_simplejwt.token_blacklist.models import (
            OutstandingToken,
        )

        old_record = OutstandingToken.objects.get(
            token=self.refresh_token
        )

        self.assertTrue(
            BlacklistedToken.objects.filter(
                token=old_record
            ).exists()
        )

        second_response = self.refresh_request(
            self.refresh_token
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_new_refresh_token_can_be_used(self):
        first_response = self.refresh_request(
            self.refresh_token
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        new_refresh = first_response.data["refresh"]

        second_response = self.refresh_request(new_refresh)

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", second_response.data)
        self.assertIn("refresh", second_response.data)

    def test_invalid_refresh_token_is_rejected(self):
        response = self.refresh_request(
            "this-is-not-a-valid-refresh-token"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_expired_refresh_token_is_rejected(self):
        expired_token = RefreshToken.for_user(self.user)

        expired_token.set_exp(
            from_time=timezone.now(),
            lifetime=timedelta(seconds=-1),
        )

        response = self.refresh_request(str(expired_token))

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_access_token_cannot_be_used_as_refresh(self):
        access_token = RefreshToken.for_user(
            self.user
        ).access_token

        response = self.refresh_request(str(access_token))

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
