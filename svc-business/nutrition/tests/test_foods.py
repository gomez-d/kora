
import uuid

from rest_framework import status
from rest_framework.test import APITestCase

from nutrition.models import (
    Food,
    FoodCategory,
    FoodNutrient,
)
from nutrition.tests.utils import authenticate_test_client


class FoodTests(APITestCase):
    def setUp(self):
        self.category = FoodCategory.objects.create(
            name="Frutas",
            description="Frutas frescas",
        )

        self.food = self.create_food(
            name="Manzana",
            description="Manzana fresca",
        )

        authenticate_test_client(
            self.client,
            user_id=uuid.uuid4(),
            permissions=[
                "foods.read",
                "foods.create",
                "foods.update",
                "foods.delete",
            ],
        )

    def complete_nutrients(self):
        return [
            {
                "nutrient_type": "CALORIES",
                "amount": 52,
                "unit": "KCAL",
            },
            {
                "nutrient_type": "PROTEIN",
                "amount": 0.4,
                "unit": "G",
            },
            {
                "nutrient_type": "CARBOHYDRATES",
                "amount": 15,
                "unit": "G",
            },
            {
                "nutrient_type": "FAT",
                "amount": 0.1,
                "unit": "G",
            },
            {
                "nutrient_type": "FIBER",
                "amount": 2.4,
                "unit": "G",
            },
            {
                "nutrient_type": "SUGAR",
                "amount": 10,
                "unit": "G",
            },
            {
                "nutrient_type": "SODIUM",
                "amount": 1,
                "unit": "MG",
            },
        ]

    def create_food(
        self,
        name="Pera",
        description="Pera fresca",
        serving_size=100,
        nutrients=None,
    ):
        food = Food.objects.create(
            category=self.category,
            name=name,
            description=description,
            serving_size=serving_size,
            serving_unit="G",
        )

        if nutrients is None:
            nutrients = self.complete_nutrients()

        for nutrient in nutrients:
            FoodNutrient.objects.create(
                food=food,
                **nutrient,
            )

        return food

    def food_payload(self, **overrides):
        payload = {
            "category_id": str(self.category.id),
            "name": "Manzana actualizada",
            "description": "Manzana fresca actualizada",
            "serving_size": 100,
            "serving_unit": "G",
            "nutrients": self.complete_nutrients(),
        }
        payload.update(overrides)
        return payload

    def assert_validation_error(self, response, field):
        self.assertIn("errors", response.data)
        self.assertIn(field, response.data["errors"])

    def test_create_food_with_nutrients(self):
        payload = {
            "category_id": str(self.category.id),
            "name": "Pera",
            "description": "Pera fresca",
            "serving_size": 100,
            "serving_unit": "G",
            "nutrients": self.complete_nutrients(),
        }

        response = self.client.post(
            "/api/foods/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Food.objects.count(), 2)
        self.assertEqual(FoodNutrient.objects.count(), 14)
        self.assertEqual(response.data["name"], "PERA")
        self.assertEqual(len(response.data["nutrients"]), 7)

    def test_create_food_without_nutrients(self):
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
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_validation_error(response, "nutrients")
        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(FoodNutrient.objects.count(), 7)

    def test_create_food_with_empty_name(self):
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
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_validation_error(response, "name")
        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(FoodNutrient.objects.count(), 7)

    def test_create_food_with_zero_serving_size(self):
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
        self.assert_validation_error(response, "serving_size")
        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(FoodNutrient.objects.count(), 7)

    def test_create_food_with_negative_nutrient_amount(self):
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
        self.assert_validation_error(response, "nutrients")
        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(FoodNutrient.objects.count(), 7)

    def test_create_food_with_invalid_nutrient_type(self):
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
        self.assert_validation_error(response, "nutrients")
        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(FoodNutrient.objects.count(), 7)

    def test_create_food_with_invalid_serving_unit(self):
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
        self.assert_validation_error(response, "serving_unit")
        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(FoodNutrient.objects.count(), 7)

    def test_create_food_with_invalid_nutrient_unit(self):
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
        self.assert_validation_error(response, "nutrients")
        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(FoodNutrient.objects.count(), 7)

    def test_create_food_with_nonexistent_category(self):
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
        self.assert_validation_error(response, "category_id")
        self.assertEqual(Food.objects.count(), 1)
        self.assertEqual(FoodNutrient.objects.count(), 7)

    def test_create_food_with_duplicate_name(self):
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
        self.assert_validation_error(response, "name")
        self.assertEqual(Food.objects.count(), 1)

    def test_create_food_with_duplicate_nutrient_type(self):
        payload = {
            "category_id": str(self.category.id),
            "name": "Pera",
            "description": "Pera fresca",
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
        self.assert_validation_error(response, "nutrients")
        self.assertEqual(Food.objects.count(), 1)

    def test_create_food_with_different_case_name(self):
        payload = {
            "category_id": str(self.category.id),
            "name": "manzana",
            "description": "Otra manzana",
            "serving_size": 100,
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
        self.assert_validation_error(response, "name")
        self.assertEqual(Food.objects.count(), 1)

    def test_update_food_with_put(self):
        payload = self.food_payload()

        response = self.client.put(
            f"/api/foods/{self.food.id}/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.food.refresh_from_db()
        self.assertEqual(self.food.name, "MANZANA ACTUALIZADA")
        self.assertEqual(
            self.food.description,
            "MANZANA FRESCA ACTUALIZADA",
        )
        self.assertEqual(str(self.food.serving_size), "100.00")

        nutrients = list(self.food.nutrients.order_by("nutrient_type"))
        self.assertEqual(len(nutrients), 7)
        self.assertEqual(
            {nutrient.nutrient_type for nutrient in nutrients},
            {
                "CALORIES",
                "PROTEIN",
                "CARBOHYDRATES",
                "FAT",
                "FIBER",
                "SUGAR",
                "SODIUM",
            },
        )

    def test_update_food_with_patch(self):
        original_description = self.food.description
        original_serving_size = self.food.serving_size
        original_nutrients = list(
            self.food.nutrients.values_list(
                "nutrient_type",
                "amount",
                "unit",
            )
        )

        response = self.client.patch(
            f"/api/foods/{self.food.id}/",
            {"name": "Manzana verde"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.food.refresh_from_db()
        self.assertEqual(self.food.name, "MANZANA VERDE")
        self.assertEqual(self.food.description, original_description)
        self.assertEqual(self.food.serving_size, original_serving_size)
        self.assertEqual(
            list(
                self.food.nutrients.values_list(
                    "nutrient_type",
                    "amount",
                    "unit",
                )
            ),
            original_nutrients,
        )

    def test_update_food_with_zero_serving_size(self):
        response = self.client.patch(
            f"/api/foods/{self.food.id}/",
            {"serving_size": 0},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.food.refresh_from_db()
        self.assertEqual(str(self.food.serving_size), "100.00")

    def test_update_food_with_duplicate_nutrient_types(self):
        original_name = self.food.name
        original_nutrients = list(
            self.food.nutrients.values_list(
                "nutrient_type",
                "amount",
                "unit",
            )
        )

        payload = {
            "name": "Manzana modificada",
            "nutrients": [
                {
                    "nutrient_type": "CALORIES",
                    "amount": 60,
                    "unit": "KCAL",
                },
                {
                    "nutrient_type": "CALORIES",
                    "amount": 65,
                    "unit": "KCAL",
                },
            ],
        }

        response = self.client.patch(
            f"/api/foods/{self.food.id}/",
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.food.refresh_from_db()
        self.assertEqual(self.food.name, original_name)
        self.assertEqual(
            list(
                self.food.nutrients.values_list(
                    "nutrient_type",
                    "amount",
                    "unit",
                )
            ),
            original_nutrients,
        )

    def test_update_food_with_duplicate_name(self):
        other_food = self.create_food(
            name="Pera",
            description="Pera fresca",
        )

        response = self.client.patch(
            f"/api/foods/{self.food.id}/",
            {"name": other_food.name},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_validation_error(response, "name")

        self.food.refresh_from_db()
        self.assertEqual(self.food.name, "Manzana")

    def test_update_food_with_its_current_name(self):
        response = self.client.patch(
            f"/api/foods/{self.food.id}/",
            {"name": self.food.name},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_nonexistent_food(self):
        response = self.client.patch(
            f"/api/foods/{uuid.uuid4()}/",
            {"name": "Pera"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_food_without_consumption_records(self):
        response = self.client.delete(
            f"/api/foods/{self.food.id}/",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Food.objects.filter(id=self.food.id).exists()
        )
        self.assertFalse(
            FoodNutrient.objects.filter(food_id=self.food.id).exists()
        )

    def test_delete_nonexistent_food(self):
        response = self.client.delete(
            f"/api/foods/{uuid.uuid4()}/",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_deleted_food_returns_not_found(self):
        food_id = self.food.id

        delete_response = self.client.delete(
            f"/api/foods/{food_id}/",
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        get_response = self.client.get(
            f"/api/foods/{food_id}/",
        )

        self.assertEqual(
            get_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
