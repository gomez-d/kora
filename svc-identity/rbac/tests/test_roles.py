from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from rbac.models import Role


class RoleTests(APITestCase):

    def setUp(self):
        self.roles_url = reverse("roles")

        self.role = Role.objects.create(
            name="Admin",
            description="Administrator role"
        )

        self.role_detail_url = reverse(
            "role-detail",
            kwargs={"role_id": self.role.id}
        )

    def test_create_role(self):
        data = {
            "name": "Nutritionist",
            "description": "Nutritionist role"
        }

        response = self.client.post(
            self.roles_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertTrue(
            Role.objects.filter(name="Nutritionist").exists()
        )

    def test_create_role_with_duplicate_name(self):
        data = {
            "name": "Admin",
            "description": "Another administrator role"
        }

        response = self.client.post(
            self.roles_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_get_all_roles(self):
        response = self.client.get(self.roles_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertGreaterEqual(len(response.data["data"]), 1)

    def test_get_role_by_id(self):
        response = self.client.get(self.role_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(
            response.data["data"]["name"],
            self.role.name
        )

    def test_get_nonexistent_role(self):
        url = reverse(
            "role-detail",
            kwargs={"role_id": "00000000-0000-0000-0000-000000000000"}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])

    def test_update_role(self):
        data = {
            "name": "Administrator",
            "description": "Updated administrator role"
        }

        response = self.client.put(
            self.role_detail_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        self.role.refresh_from_db()
        self.assertEqual(self.role.name, "Administrator")

    def test_partial_update_role(self):
        data = {
            "description": "Updated description"
        }

        response = self.client.patch(
            self.role_detail_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.role.refresh_from_db()
        self.assertEqual(self.role.description, "Updated description")
        self.assertEqual(self.role.name, "Admin")

    def test_delete_role(self):
        response = self.client.delete(self.role_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(
            Role.objects.filter(id=self.role.id).exists()
        )

    def test_delete_nonexistent_role(self):
        url = reverse(
            "role-detail",
            kwargs={"role_id": "00000000-0000-0000-0000-000000000000"}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data["success"])
