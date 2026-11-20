from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from rbac.models import Role, UserRole
from users.models import User

class RoleIntegrationTests(APITestCase):
    """
    Integration tests for HU-028 role behavior.
    """

    def setUp(self):
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
            email="roleuser@example.com",
            password="TestPassword123!"
        )

        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="TestPassword123!"
        )

        self.admin = User.objects.create_user(
            email="roleadmin@example.com",
            password="TestPassword123!"
        )

        self.user_assignment = UserRole.objects.create(
            user=self.user,
            role=self.user_role
        )

        UserRole.objects.create(
            user=self.other_user,
            role=self.user_role
        )

        UserRole.objects.create(
            user=self.admin,
            role=self.admin_role
        )

    def test_user_role_assignment_is_persisted(self):
        """
        Verify that a user-role association is persisted.
        """

        assignment = UserRole.objects.get(
            id=self.user_assignment.id
        )

        self.assertEqual(
            assignment.user_id,
            self.user.id
        )

        self.assertEqual(
            assignment.role_id,
            self.user_role.id
        )

        self.assertTrue(
            self.user.roles.filter(
                name="USER"
            ).exists()
        )

    def test_user_can_consult_own_roles(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "user-roles-query",
            kwargs={
                "user_id": self.user.id
            }
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            "USER",
            response.data["roles"]
        )

    def test_user_cannot_consult_other_user_roles(self):
        self.client.force_authenticate(user=self.user)

        url = reverse(
            "user-roles-query",
            kwargs={
                "user_id": self.other_user.id
            }
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_consult_other_user_roles(self):
        self.client.force_authenticate(user=self.admin)

        url = reverse(
            "user-roles-query",
            kwargs={
                "user_id": self.other_user.id
            }
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            "USER",
            response.data["roles"]
        )

    def test_user_cannot_assign_admin_role_to_self(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("user-roles")

        data = {
            "user": str(self.user.id),
            "role": str(self.admin_role.id)
        }

        response = self.client.post(
            url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertFalse(
            UserRole.objects.filter(
                user=self.user,
                role=self.admin_role
            ).exists()
        )