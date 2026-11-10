from django.test import TestCase

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
