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
        self.assertEqual(FoodCategory.objects.get().name, "Frutas")

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
