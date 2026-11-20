from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserDetailTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="User"
        )

        self.user_detail_url = reverse(
            "user-detail",
            kwargs={"user_id": self.user.id}
        )

        self.users_url = reverse("users")

    def test_get_user_by_id(self):
        response = self.client.get(self.user_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(
            response.data["data"]["user_id"],
            str(self.user.id)
        )

    def test_get_nonexistent_user(self):
        url = reverse(
            "user-detail",
            kwargs={"user_id": "00000000-0000-0000-0000-000000000000"}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_get_all_active_users(self):
        User.objects.create_user(
            email="another@example.com",
            password="TestPassword123!",
            first_name="Another",
            last_name="User"
        )

        response = self.client.get(self.users_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 2)

    def test_get_all_users_excludes_inactive_users(self):
        inactive_user = User.objects.create_user(
            email="inactive@example.com",
            password="TestPassword123!",
            first_name="Inactive",
            last_name="User",
            is_active=False
        )

        response = self.client.get(self.users_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)

        returned_ids = [
            user["user_id"] for user in response.data["data"]
        ]

        self.assertNotIn(str(inactive_user.id), returned_ids)

    def test_get_inactive_user_returns_not_found(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.get(self.user_detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
