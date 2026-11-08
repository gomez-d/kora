from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserUpdateTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="User"
        )

        self.update_url = reverse(
            "user-update",
            kwargs={"user_id": self.user.id}
        )

        self.valid_data = {
            "email": "updated@example.com",
            "first_name": "Updated",
            "last_name": "User",
            "date_of_birth": "1995-05-15"
        }

    def test_update_user(self):
        response = self.client.put(
            self.update_url,
            self.valid_data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        self.user.refresh_from_db()

        self.assertEqual(self.user.email, "updated@example.com")
        self.assertEqual(self.user.first_name, "Updated")

    def test_partial_update_user(self):
        response = self.client.patch(
            self.update_url,
            {"first_name": "New Name"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, "New Name")
        self.assertEqual(self.user.email, "testuser@example.com")

    def test_update_nonexistent_user(self):
        url = reverse(
            "user-update",
            kwargs={"user_id": "00000000-0000-0000-0000-000000000000"}
        )

        response = self.client.put(
            url,
            self.valid_data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_update_user_with_duplicate_email(self):
        User.objects.create_user(
            email="another@example.com",
            password="TestPassword123!",
            first_name="Another",
            last_name="User"
        )

        response = self.client.patch(
            self.update_url,
            {"email": "another@example.com"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_update_user_with_future_date_of_birth(self):
        from datetime import timedelta
        from django.utils import timezone

        future_date = timezone.localdate() + timedelta(days=1)

        response = self.client.patch(
            self.update_url,
            {"date_of_birth": future_date.isoformat()},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("date_of_birth", response.data["errors"])
