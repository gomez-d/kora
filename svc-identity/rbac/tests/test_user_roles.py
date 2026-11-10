from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from rbac.models import Role, UserRole


class UserRoleTests(APITestCase):

    def setUp(self):
        self.user_roles_url = reverse("user-roles")

        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="User"
        )

        self.role = Role.objects.create(
            name="Admin",
            description="Administrator role"
        )

        self.user_role = UserRole.objects.create(
            user=self.user,
            role=self.role
        )

        self.user_role_detail_url = reverse(
            "user-role-detail",
            kwargs={"user_role_id": self.user_role.id}
        )

    def test_assign_role_to_user(self):
        another_user = User.objects.create_user(
            email="another@example.com",
            password="TestPassword123!",
            first_name="Another",
            last_name="User"
        )

        data = {
            "user": str(another_user.id),
            "role": str(self.role.id)
        }

        response = self.client.post(
            self.user_roles_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertTrue(
            UserRole.objects.filter(
                user=another_user,
                role=self.role
            ).exists()
        )

    def test_assign_role_with_nonexistent_user(self):
        data = {
            "user": "00000000-0000-0000-0000-000000000000",
            "role": str(self.role.id)
        }

        response = self.client.post(
            self.user_roles_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_assign_nonexistent_role_to_user(self):
        data = {
            "user": str(self.user.id),
            "role": "00000000-0000-0000-0000-000000000000"
        }

        response = self.client.post(
            self.user_roles_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_assign_duplicate_role_to_user(self):
        data = {
            "user": str(self.user.id),
            "role": str(self.role.id)
        }

        response = self.client.post(
            self.user_roles_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_get_all_user_role_assignments(self):
        response = self.client.get(self.user_roles_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertGreaterEqual(len(response.data["data"]), 1)

    def test_get_user_role_assignment_by_id(self):
        response = self.client.get(self.user_role_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_get_nonexistent_user_role_assignment(self):
        url = reverse(
            "user-role-detail",
            kwargs={"user_role_id": "00000000-0000-0000-0000-000000000000"}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_remove_role_from_user(self):
        response = self.client.delete(self.user_role_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(
            UserRole.objects.filter(id=self.user_role.id).exists()
        )

        self.assertTrue(User.objects.filter(id=self.user.id).exists())
        self.assertTrue(Role.objects.filter(id=self.role.id).exists())

    def test_remove_nonexistent_user_role_assignment(self):
        url = reverse(
            "user-role-detail",
            kwargs={"user_role_id": "00000000-0000-0000-0000-000000000000"}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
