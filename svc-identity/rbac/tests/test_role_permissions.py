from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from rbac.models import Role, Permission, RolePermission


class RolePermissionTests(APITestCase):

    def setUp(self):
        self.role_permissions_url = reverse("role-permissions")

        self.role = Role.objects.create(
            name="Admin",
            description="Administrator role"
        )

        self.permission = Permission.objects.create(
            name="View Users",
            resource="users",
            action="read",
            description="Allows viewing users"
        )

        self.role_permission = RolePermission.objects.create(
            role=self.role,
            permission=self.permission
        )

        self.role_permission_detail_url = reverse(
            "role-permission-detail",
            kwargs={"role_permission_id": self.role_permission.id}
        )

    def test_assign_permission_to_role(self):
        another_permission = Permission.objects.create(
            name="Create Users",
            resource="users",
            action="create",
            description="Allows creating users"
        )

        data = {
            "role": str(self.role.id),
            "permission": str(another_permission.id)
        }

        response = self.client.post(
            self.role_permissions_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertTrue(
            RolePermission.objects.filter(
                role=self.role,
                permission=another_permission
            ).exists()
        )

    def test_assign_permission_to_nonexistent_role(self):
        data = {
            "role": "00000000-0000-0000-0000-000000000000",
            "permission": str(self.permission.id)
        }

        response = self.client.post(
            self.role_permissions_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_assign_nonexistent_permission_to_role(self):
        data = {
            "role": str(self.role.id),
            "permission": "00000000-0000-0000-0000-000000000000"
        }

        response = self.client.post(
            self.role_permissions_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_assign_duplicate_permission_to_role(self):
        data = {
            "role": str(self.role.id),
            "permission": str(self.permission.id)
        }

        response = self.client.post(
            self.role_permissions_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_get_all_role_permission_assignments(self):
        response = self.client.get(self.role_permissions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertGreaterEqual(len(response.data["data"]), 1)

    def test_get_role_permission_assignment_by_id(self):
        response = self.client.get(self.role_permission_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_get_nonexistent_role_permission_assignment(self):
        url = reverse(
            "role-permission-detail",
            kwargs={
                "role_permission_id": "00000000-0000-0000-0000-000000000000"
            }
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_remove_permission_from_role(self):
        response = self.client.delete(self.role_permission_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(
            RolePermission.objects.filter(
                id=self.role_permission.id
            ).exists()
        )

        self.assertTrue(Role.objects.filter(id=self.role.id).exists())
        self.assertTrue(
            Permission.objects.filter(id=self.permission.id).exists()
        )

    def test_remove_nonexistent_role_permission_assignment(self):
        url = reverse(
            "role-permission-detail",
            kwargs={
                "role_permission_id": "00000000-0000-0000-0000-000000000000"
            }
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
