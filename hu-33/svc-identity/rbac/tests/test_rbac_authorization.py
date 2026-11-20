from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from rbac.models import (
    Permission,
    Role,
    RolePermission,
    UserRole,
)
from users.models import User


class RbacAuthorizationTests(APITestCase):
    """
    Authorization tests for HU-029 RBAC behavior.

    These tests verify administrative access, regular user restrictions,
    ownership isolation, and unauthenticated access handling.
    """

    def setUp(self):
        """
        Create users, roles, and permissions required by the
        authorization scenarios under test.
        """

        # Obtain the standard Kora roles.
        self.user_role, _ = Role.objects.get_or_create(
            name="USER",
            defaults={
                "description": "Standard Kora user role."
            }
        )

        self.admin_role, _ = Role.objects.get_or_create(
            name="ADMIN",
            defaults={
                "description": "Kora administrator role."
            }
        )

        # Create the permissions required by the tested endpoints.
        self.users_read_self, _ = Permission.objects.get_or_create(
            name="users.read_self",
            defaults={
                "resource": "users",
                "action": "read_self",
                "description": (
                    "Read the authenticated user's own information."
                ),
            }
        )

        self.users_read_any, _ = Permission.objects.get_or_create(
            name="users.read_any",
            defaults={
                "resource": "users",
                "action": "read_any",
                "description": "Read information from any user.",
            }
        )

        self.roles_read, _ = Permission.objects.get_or_create(
            name="roles.read",
            defaults={
                "resource": "roles",
                "action": "read",
                "description": "Read system roles.",
            }
        )

        # Regular users may only read their own information.
        RolePermission.objects.get_or_create(
            role=self.user_role,
            permission=self.users_read_self
        )

        # Administrators may read their own information,
        # other users, and RBAC roles.
        RolePermission.objects.get_or_create(
            role=self.admin_role,
            permission=self.users_read_self
        )

        RolePermission.objects.get_or_create(
            role=self.admin_role,
            permission=self.users_read_any
        )

        RolePermission.objects.get_or_create(
            role=self.admin_role,
            permission=self.roles_read
        )

        # Create two regular users to verify ownership isolation.
        self.user_a = User.objects.create_user(
            email="rbac_user_a@example.com",
            password="TestPassword123!"
        )

        self.user_b = User.objects.create_user(
            email="rbac_user_b@example.com",
            password="TestPassword123!"
        )

        # Create the administrator used by administrative scenarios.
        self.admin = User.objects.create_user(
            email="rbac_admin@example.com",
            password="TestPassword123!"
        )

        # Assign the corresponding roles.
        UserRole.objects.create(
            user=self.user_a,
            role=self.user_role
        )

        UserRole.objects.create(
            user=self.user_b,
            role=self.user_role
        )

        UserRole.objects.create(
            user=self.admin,
            role=self.admin_role
        )

        # Resolve protected endpoint URLs using their configured names.
        self.users_url = reverse("users")
        self.roles_url = reverse("roles")

    def test_admin_can_list_users(self):
        """
        Verify that an administrator can access the protected user list.
        """

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            self.users_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_regular_user_cannot_list_users(self):
        """
        Verify that a regular user cannot execute the administrative
        user-list operation.
        """

        self.client.force_authenticate(
            user=self.user_a
        )

        response = self.client.get(
            self.users_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_regular_user_can_read_own_information(self):
        """
        Verify that a regular user can access their own private
        user information.
        """

        self.client.force_authenticate(
            user=self.user_a
        )

        url = reverse(
            "user-detail",
            kwargs={
                "user_id": self.user_a.id
            }
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_regular_user_cannot_read_another_user(self):
        """
        Verify that a regular user cannot access another user's
        private information by using that user's identifier.
        """

        self.client.force_authenticate(
            user=self.user_a
        )

        url = reverse(
            "user-detail",
            kwargs={
                "user_id": self.user_b.id
            }
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_admin_can_read_another_user(self):
        """
        Verify that an administrator with users.read_any can
        access another user's information.
        """

        self.client.force_authenticate(
            user=self.admin
        )

        url = reverse(
            "user-detail",
            kwargs={
                "user_id": self.user_a.id
            }
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_can_read_roles(self):
        """
        Verify that an administrator can access protected RBAC roles.
        """

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            self.roles_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_regular_user_cannot_read_roles(self):
        """
        Verify that a regular user cannot access administrative
        RBAC information.
        """

        self.client.force_authenticate(
            user=self.user_a
        )

        response = self.client.get(
            self.roles_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_unauthenticated_user_cannot_list_users(self):
        """
        Verify that a protected endpoint rejects requests without
        authentication using HTTP 401.
        """

        response = self.client.get(
            self.users_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        self.assertEqual(
            response.data["code"],
            "unauthorized"
        )