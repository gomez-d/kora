from django.test import TestCase

from rbac.models import Role, UserRole
from users.models import User
from users.serializers import UserRegistrationSerializer


class UserRegistrationTests(TestCase):

    def test_password_is_not_stored_in_plain_text(self):
        raw_password = "TestPassword123!"

        data = {
            "email": "test@example.com",
            "password": raw_password,
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1995-05-15"
        }

        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()

        self.assertNotEqual(user.password, raw_password)
        self.assertTrue(user.check_password(raw_password))

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            email="duplicate@example.com",
            password="TestPassword123!",
            first_name="First",
            last_name="User"
        )

        data = {
            "email": "duplicate@example.com",
            "password": "AnotherPassword123!",
            "first_name": "Second",
            "last_name": "User",
            "date_of_birth": "1995-05-15"
        }

        serializer = UserRegistrationSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_registration_with_invalid_date_of_birth(self):
        data = {
            "email": "invalid@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "invalid-date"
        }

        serializer = UserRegistrationSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("date_of_birth", serializer.errors)

    def test_registration_with_future_date_of_birth(self):
        from datetime import timedelta
        from django.utils import timezone

        future_date = timezone.localdate() + timedelta(days=1)

        data = {
            "email": "future@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": future_date.isoformat()
        }

        serializer = UserRegistrationSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("date_of_birth", serializer.errors)

    def test_registration_with_null_date_of_birth(self):
        data = {
            "email": "nullbirth@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": None
        }

        serializer = UserRegistrationSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("date_of_birth", serializer.errors)

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

        def test_registered_user_receives_default_user_role(self):
            data = {
                "email": "roleuser@example.com",
                "password": "TestPassword123!",
                "first_name": "Role",
                "last_name": "User",
                "date_of_birth": "1995-05-15"
            }

            serializer = UserRegistrationSerializer(data=data)

            self.assertTrue(
                serializer.is_valid(),
                serializer.errors
            )

            user = serializer.save()

            self.assertTrue(
                UserRole.objects.filter(
                    user=user,
                    role=self.user_role
                ).exists()
            )

            self.assertTrue(
                user.roles.filter(
                    name="USER"
                ).exists()
            )

            self.assertFalse(
                user.roles.filter(
                    name="ADMIN"
                ).exists()
            )

    def test_registration_rejects_role_field(self):
        data = {
            "email": "unauthorized-role@example.com",
            "password": "TestPassword123!",
            "first_name": "Unauthorized",
            "last_name": "Role",
            "date_of_birth": "1995-05-15",
            "role": "ADMIN"
        }

        serializer = UserRegistrationSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("role", serializer.errors)

        self.assertFalse(
            User.objects.filter(
                email="unauthorized-role@example.com"
            ).exists()
        )

    def test_registration_rejects_roles_field(self):
        data = {
            "email": "unauthorized-roles@example.com",
            "password": "TestPassword123!",
            "first_name": "Unauthorized",
            "last_name": "Roles",
            "date_of_birth": "1995-05-15",
            "roles": ["ADMIN"]
        }

        serializer = UserRegistrationSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("role", serializer.errors)

        self.assertFalse(
            User.objects.filter(
                email="unauthorized-roles@example.com"
            ).exists()
        )   