from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from rbac.models import Permission


class PermissionTests(APITestCase):

    def setUp(self):
        self.permissions_url = reverse("permissions")

        self.permission = Permission.objects.create(
            name="View Users",
            resource="users",
            action="read",
            description="Allows viewing users"
        )

        self.permission_detail_url = reverse(
            "permission-detail",
            kwargs={"permission_id": self.permission.id}
        )

    def test_create_permission(self):
        data = {
            "name": "Create Users",
            "resource": "users",
            "action": "create",
            "description": "Allows creating users"
        }

        response = self.client.post(
            self.permissions_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertTrue(
            Permission.objects.filter(name="Create Users").exists()
        )

    def test_create_permission_with_duplicate_name(self):
        data = {
            "name": "View Users",
            "resource": "users",
            "action": "read",
            "description": "Another description"
        }

        response = self.client.post(
            self.permissions_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_get_all_permissions(self):
        response = self.client.get(self.permissions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertGreaterEqual(len(response.data["data"]), 1)

    def test_get_permission_by_id(self):
        response = self.client.get(self.permission_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(
            response.data["data"]["name"],
            self.permission.name
        )

    def test_get_nonexistent_permission(self):
        url = reverse(
            "permission-detail",
            kwargs={"permission_id": "00000000-0000-0000-0000-000000000000"}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_update_permission(self):
        data = {
            "name": "Manage Users",
            "resource": "users",
            "action": "manage",
            "description": "Allows managing users"
        }

        response = self.client.put(
            self.permission_detail_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        self.permission.refresh_from_db()
        self.assertEqual(self.permission.name, "Manage Users")

    def test_partial_update_permission(self):
        data = {
            "description": "Updated description"
        }

        response = self.client.patch(
            self.permission_detail_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.permission.refresh_from_db()
        self.assertEqual(self.permission.description, "Updated description")
        self.assertEqual(self.permission.name, "View Users")

    def test_delete_permission(self):
        response = self.client.delete(self.permission_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(
            Permission.objects.filter(id=self.permission.id).exists()
        )

    def test_delete_nonexistent_permission(self):
        url = reverse(
            "permission-detail",
            kwargs={"permission_id": "00000000-0000-0000-0000-000000000000"}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
