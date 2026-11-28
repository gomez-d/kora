
from unittest.mock import patch
from uuid import uuid4

from rest_framework import status
from rest_framework.test import APITestCase

from nutrition.models import FoodCategory
from nutrition.tests.utils import authenticate_test_client


@patch("nutrition.views.user_exists", return_value=True)
class InputValidationTests(APITestCase):
    """
    Verify invalid input handling for Business API endpoints.
    """

    def setUp(self):
        self.user_id = str(uuid4())

        authenticate_test_client(
            self.client,
            user_id=self.user_id,
            permissions=[
                "nutritional_profiles.create_self",
                "foods.create",
            ],
        )

        self.category = FoodCategory.objects.create(
            name="TEST CATEGORY",
            description="CATEGORY FOR INPUT VALIDATION TESTS",
        )

    def test_rejects_missing_required_user_id(self, mock_user_exists):
        payload = {
            "date_of_birth": "2000-01-01",
            "sex": "FEMALE",
            "weight": 60,
            "height": 1.65,
            "activity_level": "MODERATE",
        }

        response = self.client.post(
            "/api/nutritional-profiles/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["code"], "validation_error")
        self.assertIn("user_id", response.data["errors"])

    def test_rejects_invalid_weight_type(self, mock_user_exists):
        payload = {
            "user_id": self.user_id,
            "date_of_birth": "2000-01-01",
            "sex": "FEMALE",
            "weight": "INVALID",
            "height": 1.65,
            "activity_level": "MODERATE",
        }

        response = self.client.post(
            "/api/nutritional-profiles/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "validation_error")
        self.assertIn("weight", response.data["errors"])

    def test_rejects_weight_below_allowed_range(self, mock_user_exists):
        payload = {
            "user_id": self.user_id,
            "date_of_birth": "2000-01-01",
            "sex": "FEMALE",
            "weight": 0.50,
            "height": 1.65,
            "activity_level": "MODERATE",
        }

        response = self.client.post(
            "/api/nutritional-profiles/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "validation_error")
        self.assertIn("weight", response.data["errors"])

    def test_rejects_unexpected_field(self, mock_user_exists):
        payload = {
            "user_id": self.user_id,
            "date_of_birth": "2000-01-01",
            "sex": "FEMALE",
            "weight": 60,
            "height": 1.65,
            "activity_level": "MODERATE",
            "unexpected_field": "INVALID",
        }

        response = self.client.post(
            "/api/nutritional-profiles/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "validation_error")
        self.assertIn("unexpected_fields", response.data["errors"])

    def test_rejects_invalid_nutrient_unit(self, mock_user_exists):
        payload = {
            "category_id": str(self.category.id),
            "name": "TEST FOOD INVALID UNIT",
            "description": "TEST FOOD",
            "serving_size": 100,
            "serving_unit": "G",
            "nutrients": [
                {"nutrient_type": "CALORIES", "amount": 100, "unit": "G"},
                {"nutrient_type": "PROTEIN", "amount": 10, "unit": "G"},
                {"nutrient_type": "CARBOHYDRATES", "amount": 20, "unit": "G"},
                {"nutrient_type": "FAT", "amount": 5, "unit": "G"},
                {"nutrient_type": "FIBER", "amount": 3, "unit": "G"},
                {"nutrient_type": "SUGAR", "amount": 2, "unit": "G"},
                {"nutrient_type": "SODIUM", "amount": 100, "unit": "MG"},
            ],
        }

        response = self.client.post(
            "/api/foods/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "validation_error")
        self.assertIn("nutrients", response.data["errors"])
