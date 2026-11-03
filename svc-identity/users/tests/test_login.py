
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserLoginTests(APITestCase):
    """
    Test cases for the user login endpoint.
    """

    def setUp(self):
        self.login_url = reverse("user-login")

        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="TestPassword123!"
        )

        self.valid_credentials = {
            "username": "testuser",
            "password": "TestPassword123!"
        }

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            self.login_url,
            self.valid_credentials,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertTrue(response.data["success"])

    def test_login_with_incorrect_password(self):
        credentials = {
            "username": "testuser",
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
            "username": "nonexistent",
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

    def test_login_without_username(self):
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
            "username": "testuser"
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
