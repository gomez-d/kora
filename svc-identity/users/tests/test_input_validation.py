from rest_framework import status
from rest_framework.test import APITestCase


class InputValidationTests(APITestCase):
    """
    Verify invalid input handling for Identity API endpoints.
    """

    def test_rejects_missing_required_field(self):
        payload = {
            "email": "missing.name@example.com",
            "password": "StrongPassword123!",
            "last_name": "TEST",
            "date_of_birth": "2000-01-01",
        }

        response = self.client.post(
            "/api/users/register/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(response.data["success"])
        self.assertEqual(
            response.data["code"],
            "validation_error",
        )
        self.assertIn(
            "first_name",
            response.data["errors"],
        )

    def test_rejects_invalid_email_type_or_format(self):
        payload = {
            "email": "INVALID_EMAIL",
            "password": "StrongPassword123!",
            "first_name": "TEST",
            "last_name": "USER",
            "date_of_birth": "2000-01-01",
        }

        response = self.client.post(
            "/api/users/register/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["code"],
            "validation_error",
        )
        self.assertIn(
            "email",
            response.data["errors"],
        )

    def test_rejects_age_outside_allowed_range(self):
        payload = {
            "email": "invalid.age@example.com",
            "password": "StrongPassword123!",
            "first_name": "TEST",
            "last_name": "USER",
            "date_of_birth": "1900-01-01",
        }

        response = self.client.post(
            "/api/users/register/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["code"],
            "validation_error",
        )
        self.assertIn(
            "date_of_birth",
            response.data["errors"],
        )

    def test_rejects_whitespace_only_first_name(self):
        payload = {
            "email": "blank.name@example.com",
            "password": "StrongPassword123!",
            "first_name": "   ",
            "last_name": "USER",
            "date_of_birth": "2000-01-01",
        }

        response = self.client.post(
            "/api/users/register/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["code"],
            "validation_error",
        )
        self.assertIn(
            "first_name",
            response.data["errors"],
        )

    def test_rejects_unexpected_field(self):
        payload = {
            "email": "unexpected.field@example.com",
            "password": "StrongPassword123!",
            "first_name": "TEST",
            "last_name": "USER",
            "date_of_birth": "2000-01-01",
            "unexpected_field": "INVALID",
        }

        response = self.client.post(
            "/api/users/register/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["code"],
            "validation_error",
        )
        self.assertIn(
            "unexpected_fields",
            response.data["errors"],
        )

    def test_rejects_malformed_json(self):
        response = self.client.post(
            "/api/users/register/",
            data='{"email":',
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(response.data["success"])
        self.assertEqual(
            response.data["code"],
            "invalid_json",
        )
        self.assertEqual(
            response.data["message"],
            "Invalid JSON payload.",
        )