from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserDeactivationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="User"
        )

        self.deactivation_url = reverse(
            "user-detail",
            kwargs={"user_id": self.user.id}
        )

        self.login_url = reverse("user-login")

    def test_deactivate_user(self):
        response = self.client.delete(self.deactivation_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(
            response.data["message"],
            "User deactivated successfully."
        )

        self.user.refresh_from_db()

        self.assertFalse(self.user.is_active)
        self.assertTrue(
            User.objects.filter(id=self.user.id).exists()
        )

    def test_deactivate_nonexistent_user(self):
        url = reverse(
            "user-detail",
            kwargs={"user_id": "00000000-0000-0000-0000-000000000000"}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_deactivated_user_cannot_login(self):
        self.client.delete(self.deactivation_url)

        credentials = {
            "email": "testuser@example.com",
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
