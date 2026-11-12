from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from rbac.models import Role, UserRole
from users.models import User


class UserTokenRefreshTests(APITestCase):
    """
    Test refresh-token behavior with the current identity role context.
    """

    def setUp(self):
        self.login_url = reverse("user-login")
        self.refresh_url = reverse("token-refresh")

        self.user_role = Role.objects.get_or_create(
            name="USER",
            defaults={
                "description": "Standard Kora user role."
            }
        )[0]

        self.admin_role = Role.objects.get_or_create(
            name="ADMIN",
            defaults={
                "description": "Kora administrator role."
            }
        )[0]

        self.user = User.objects.create_user(
            email="refreshuser@example.com",
            password="TestPassword123!",
            first_name="Refresh",
            last_name="User"
        )

        UserRole.objects.create(
            user=self.user,
            role=self.user_role
        )

        self.credentials = {
            "email": "refreshuser@example.com",
            "password": "TestPassword123!"
        }

    def get_refresh_token(self):
        """
        Authenticate the test user and return the generated refresh token.
        """

        response = self.client.post(
            self.login_url,
            self.credentials,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        return response.data["data"]["refresh"]

    def test_refresh_access_token_contains_current_roles(self):
        """
        Verify that a refreshed access token contains the user's current roles.
        """

        refresh_token = self.get_refresh_token()

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": refresh_token
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        token = AccessToken(
            response.data["access"]
        )

        self.assertEqual(
            token["roles"],
            ["USER"]
        )

    def test_refresh_updates_roles_from_database(self):
        """
        Verify that role changes in PostgreSQL are reflected
        in the next access token generated from an existing refresh token.
        """

        refresh_token = self.get_refresh_token()

        UserRole.objects.create(
            user=self.user,
            role=self.admin_role
        )

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": refresh_token
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        token = AccessToken(
            response.data["access"]
        )

        self.assertCountEqual(
            token["roles"],
            ["USER", "ADMIN"]
        )

    def test_inactive_user_cannot_refresh_token(self):
        """
        Verify that an inactive user cannot obtain a new access token.
        """

        refresh_token = self.get_refresh_token()

        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": refresh_token
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )