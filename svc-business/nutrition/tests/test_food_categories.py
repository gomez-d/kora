from rest_framework import status
from rest_framework.test import APITestCase

from nutrition.models import FoodCategory


class FoodCategoryTests(APITestCase):
    def test_create_food_category(self):
        """Ä valid food category should be created successfully"""
        payload = {
            "name": "Frutas",
            "description": "Frutas frescas"
        }

        response = self.client.post(
            "/api/food-categories/",
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FoodCategory.objects.count(), 1)
        self.assertEqual(FoodCategory.objects.get().name, "FRUTAS")
        self.assertEqual(
            FoodCategory.objects.get().description, "FRUTAS FRESCAS")

    def test_create_food_category_with_empty_name(self):
        """Ä food category with an empty name should be rejected"""
        payload = {
            "name": "",
            "description": "Frutas frescas"
        }

        response = self.client.post(
            "/api/food-categories/",
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(FoodCategory.objects.count(), 0)

    def test_create_food_category_with_duplicate_name(self):
        """A category with an existing name should be rejected."""
        FoodCategory.objects.create(
            name="Frutas",
            description="Frutas frescas",
        )

        payload = {
            "name": "Frutas",
            "description": "Otras frutas",
        }

        response = self.client.post(
            "/api/food-categories/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(FoodCategory.objects.count(), 1)

    def test_create_food_category_with_different_case_name(self):
        """Category names should be unique regardless of letter case."""
        FoodCategory.objects.create(
            name="FRUTAS",
            description="FRUTAS FRESCAS",
        )

        payload = {
            "name": "frutas",
            "description": "OTRAS FRUTAS",
        }

        response = self.client.post(
            "/api/food-categories/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(FoodCategory.objects.count(), 1)
