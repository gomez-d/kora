from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User

from rbac.models import Role, UserRole


class UserLoginTests(APITestCase):
    """
    Test cases for the user login endpoint.
    """

    def setUp(self):
        self.login_url = reverse("user-login")

        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="User"
        )

        # Get de standard user role.
        self.user_role = Role.objects.get_or_create(
            name="USER",
            defaults={
                "description": "Standard Kora user role."
            }
        )[0]

        # Associate the standard role with the test user.
        UserRole.objects.get_or_create(
            user=self.user,
            role=self.user_role
        )

        self.valid_credentials = {
            "email": "testuser@example.com",
            "password": "TestPassword123!"
        }

    def test_login_with_valid_credentials_returns_tokens(self):
        response = self.client.post(
            self.login_url,
            self.valid_credentials,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])
        self.assertIn("user_id", response.data["data"])
        self.assertEqual(
            response.data["data"]["user_id"],
            str(self.user.id)
        )

    def test_login_with_incorrect_password(self):
        credentials = {
            "email": "testuser@example.com",
            "password": "WrongPassword123!"
        }

        response = self.client.post(
            self.login_url,
            credentials,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        self.assertFalse(response.data["success"])

    def test_login_with_nonexistent_user(self):
        credentials = {
            "email": "nonexistent@example.com",
            "password": "TestPassword123!"
        }

        response = self.client.post(
            self.login_url,
            credentials,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        self.assertFalse(response.data["success"])

    def test_login_with_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.login_url,
            self.valid_credentials,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        self.assertFalse(response.data["success"])

    def test_login_without_email(self):
        credentials = {
            "password": "TestPassword123!"
        }

        response = self.client.post(
            self.login_url,
            credentials,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_login_without_password(self):
        credentials = {
            "email": "testuser@example.com"
        }

        response = self.client.post(
            self.login_url,
            credentials,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_login_with_empty_credentials(self):
        response = self.client.post(
            self.login_url,
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_login_access_token_contains_current_user_roles(self):
        """
        Verify that the access token contains roles obtained
        from the identity database.
        """

        response = self.client.post(
            self.login_url,
            self.valid_credentials,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        access_token = response.data["data"]["access"]

        token = AccessToken(access_token)

        self.assertIn("roles", token)

        self.assertEqual(
            token["roles"],
            ["USER"]
        )

    def test_login_access_token_uses_roles_from_database(self):
        """
        Verify that role claims are built from the user's
        persisted role assignments.
        """

        admin_role = Role.objects.get_or_create(
            name="ADMIN",
            defaults={
                "description": "Kora administrator role."
            }
        )[0]

        UserRole.objects.create(
            user=self.user,
            role=admin_role
        )

        response = self.client.post(
            self.login_url,
            self.valid_credentials,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        token = AccessToken(
            response.data["data"]["access"]
        )

        self.assertCountEqual(
            token["roles"],
            ["USER", "ADMIN"]
        )
