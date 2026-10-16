from rest_framework import status
from rest_framework.test import APITestCase

from nutrition.models import Food, FoodCategory, FoodNutrient


class FoodTests(APITestCase):
    def setUp(self):
        self.category = FoodCategory.objects.create(
            name="Frutas",
            description="Frutas frescas"
        )

    def test_create_food_with_nutrients(self):
        """A valid food and its nutrients should be created successfully."""
        payload = {
            "category_id": str(self.category.id),
            "name": "Manzana",
            "description": "Manzana fresca",
            "serving_size": 100,
            "serving_unit": "G",
            "nutrients": [
                {
                    "nutrient_type": "CALORIES",
                    "amount": 52,
                    "unit": "KCAL",
                },
                {
                    "nutrient_type": "FIBER",
                    "amount": 2.4,
                    "unit": "G",
                },
            ],
        }

        response = self.client.post(
            "/api/foods/",
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(FoodNutrient.objects.count(), 2)
        self.assertEqual(response.data["name"], "MANZANA")
        self.assertEqual(len(response.data["nutrients"]), 2)
        self.assertEqual(Food.objects.get().description, "MANZANA FRESCA")

    def test_create_food_without_nutrients(self):
        """A food without nutrients should be rejected."""
        payload = {
            "category_id": str(self.category.id),
            "name": "Pera",
            "description": "Pera fresca",
            "serving_size": 100,
            "serving_unit": "G",
            "nutrients": [],
        }

        response = self.client.post(
            "/api/foods/",
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nutrients", response.data)
        self.assertEqual(Food.objects.count(), 0)
        self.assertEqual(FoodNutrient.objects.count(), 0)

    def test_create_food_with_empty_name(self):
        """A food with an empty name should be rejected."""
        payload = {
            "category_id": str(self.category.id),
            "name": "",
            "description": "Pera fresca",
            "serving_size": 100,
            "serving_unit": "G",
            "nutrients": [
                {
                    "nutrient_type": "CALORIES",
                    "amount": 57,
                    "unit": "KCAL",
                },
            ],
        }

        response = self.client.post(
            "/api/foods/",
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Food.objects.count(), 0)
        self.assertEqual(FoodNutrient.objects.count(), 0)

    def test_create_food_with_zero_serving_size(self):
        """A food with a zero serving size should be rejected."""
        payload = {
            "category_id": str(self.category.id),
            "name": "Pera",
            "description": "Pera fresca",
            "serving_size": 0,
            "serving_unit": "G",
            "nutrients": [
                {
                    "nutrient_type": "CALORIES",
                    "amount": 57,
                    "unit": "KCAL",
                },
            ],
        }

        response = self.client.post(
            "/api/foods/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("serving_size", response.data)
        self.assertEqual(Food.objects.count(), 0)
        self.assertEqual(FoodNutrient.objects.count(), 0)

    def test_create_food_with_negative_nutrient_amount(self):
        """A food with a negative nutrient amount should be rejected."""
        payload = {
            "category_id": str(self.category.id),
            "name": "Pera",
            "description": "Pera fresca",
            "serving_size": 100,
            "serving_unit": "G",
            "nutrients": [
                {
                    "nutrient_type": "CALORIES",
                    "amount": -10,
                    "unit": "KCAL",
                },
            ],
        }

        response = self.client.post(
            "/api/foods/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nutrients", response.data)
        self.assertEqual(Food.objects.count(), 0)
        self.assertEqual(FoodNutrient.objects.count(), 0)

    def test_create_food_with_invalid_nutrient_type(self):
        """A food with an invalid nutrient type should be rejected."""
        payload = {
            "category_id": str(self.category.id),
            "name": "Pera",
            "description": "Pera fresca",
            "serving_size": 100,
            "serving_unit": "G",
            "nutrients": [
                {
                    "nutrient_type": "VITAMINS",
                    "amount": 10,
                    "unit": "G",
                },
            ],
        }

        response = self.client.post(
            "/api/foods/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nutrients", response.data)
        self.assertEqual(Food.objects.count(), 0)
        self.assertEqual(FoodNutrient.objects.count(), 0)

    def test_create_food_with_invalid_serving_unit(self):
        """A food with an invalid serving unit should be rejected."""
        payload = {
            "category_id": str(self.category.id),
            "name": "Pera",
            "description": "Pera fresca",
            "serving_size": 100,
            "serving_unit": "OZ",
            "nutrients": [
                {
                    "nutrient_type": "CALORIES",
                    "amount": 57,
                    "unit": "KCAL",
                },
            ],
        }

        response = self.client.post(
            "/api/foods/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("serving_unit", response.data)
        self.assertEqual(Food.objects.count(), 0)
        self.assertEqual(FoodNutrient.objects.count(), 0)

    def test_create_food_with_invalid_nutrient_unit(self):
        """A food with an invalid nutrient unit should be rejected."""
        payload = {
            "category_id": str(self.category.id),
            "name": "Pera",
            "description": "Pera fresca",
            "serving_size": 100,
            "serving_unit": "G",
            "nutrients": [
                {
                    "nutrient_type": "CALORIES",
                    "amount": 57,
                    "unit": "LBS",
                },
            ],
        }

        response = self.client.post(
            "/api/foods/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nutrients", response.data)
        self.assertEqual(Food.objects.count(), 0)
        self.assertEqual(FoodNutrient.objects.count(), 0)

    def test_create_food_with_nonexistent_category(self):
        """A food with a nonexistent category should be rejected."""
        import uuid

        payload = {
            "category_id": str(uuid.uuid4()),
            "name": "Pera",
            "description": "Pera fresca",
            "serving_size": 100,
            "serving_unit": "G",
            "nutrients": [
                {
                    "nutrient_type": "CALORIES",
                    "amount": 57,
                    "unit": "KCAL",
                },
            ],
        }

        response = self.client.post(
            "/api/foods/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category_id", response.data)
        self.assertEqual(Food.objects.count(), 0)
        self.assertEqual(FoodNutrient.objects.count(), 0)

    def test_create_food_with_duplicate_name(self):
        """A food with an existing name should be rejected."""
        Food.objects.create(
            category=self.category,
            name="Manzana",
            description="Manzana fresca",
            serving_size=100,
            serving_unit="G",
        )

        payload = {
            "category_id": str(self.category.id),
            "name": "Manzana",
            "description": "Otra manzana",
            "serving_size": 150,
            "serving_unit": "G",
            "nutrients": [
                {
                    "nutrient_type": "CALORIES",
                    "amount": 52,
                    "unit": "KCAL",
                },
            ],
        }

        response = self.client.post(
            "/api/foods/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(FoodNutrient.objects.count(), 0)

    def test_create_food_with_duplicate_nutrient_type(self):
        """A food with duplicate nutrient types should be rejected."""
        payload = {
            "category_id": str(self.category.id),
            "name": "Manzana",
            "description": "Manzana fresca",
            "serving_size": 100,
            "serving_unit": "G",
            "nutrients": [
                {
                    "nutrient_type": "FAT",
                    "amount": 1,
                    "unit": "G",
                },
                {
                    "nutrient_type": "FAT",
                    "amount": 2,
                    "unit": "G",
                },
            ],
        }

        response = self.client.post(
            "/api/foods/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nutrients", response.data)
        self.assertEqual(Food.objects.count(), 0)
        self.assertEqual(FoodNutrient.objects.count(), 0)

    def test_create_food_with_different_case_name(self):
        """Food names should be unique regardless of letter case."""
        Food.objects.create(
            category=self.category,
            name="MANZANA",
            description="MANZANA FRESCA",
            serving_size=100,
            serving_unit="G",
        )

        payload = {
            "category_id": str(self.category.id),
            "name": "manzana",
            "description": "OTRA MANZANA",
            "serving_size": 150,
            "serving_unit": "G",
            "nutrients": [
                {
                    "nutrient_type": "CALORIES",
                    "amount": 52,
                    "unit": "KCAL",
                },
            ],
        }

        response = self.client.post("/api/foods/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(Food.objects.count(), 1)
