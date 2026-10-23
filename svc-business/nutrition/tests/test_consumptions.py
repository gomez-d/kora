from datetime import timedelta
import uuid

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from nutrition.models import (
    ConsumptionRecord,
    ConsumptionItem,
    Food,
    FoodCategory,
)


class ConsumptionRecordTests(APITestCase):
    def setUp(self):
        self.category = FoodCategory.objects.create(
            name="FRUTAS",
            description="FRUTAS FRESCAS",
        )

        self.food = Food.objects.create(
            category=self.category,
            name="MANZANA",
            description="MANZANA FRESCA",
            serving_size=100,
            serving_unit="G",
        )

        self.url = "/api/consumptions/"

        self.payload = {
            "user_id": str(uuid.uuid4()),
            "consumed_at": timezone.now().isoformat(),
            "notes": "Consumo de prueba",
            "consumption_items": [
                {
                    "food_id": str(self.food.id),
                    "quantity": "1.00",
                    "calories": "52.00",
                    "protein": "0.26",
                    "carbohydrates": "13.81",
                    "fat": "0.17",
                    "fiber": "2.40",
                    "sugar": "10.39",
                    "sodium": "1.00",
                }
            ],
        }

    def test_create_consumption_with_one_food(self):
        """A valid consumption with one food should be created."""
        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConsumptionRecord.objects.count(), 1)
        self.assertEqual(ConsumptionItem.objects.count(), 1)
        self.assertEqual(response.data["notes"], "CONSUMO DE PRUEBA")

    def test_create_consumption_with_multiple_foods(self):
        """A consumption with multiple foods should be created."""
        second_food = Food.objects.create(
            category=self.category,
            name="PERA",
            description="PERA FRESCA",
            serving_size=100,
            serving_unit="G",
        )

        second_item = self.payload["consumption_items"][0].copy()
        second_item["food_id"] = str(second_food.id)
        self.payload["consumption_items"].append(second_item)

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConsumptionRecord.objects.count(), 1)
        self.assertEqual(ConsumptionItem.objects.count(), 2)

    def test_create_consumption_with_zero_quantity(self):
        """A zero quantity should be rejected."""
        self.payload["consumption_items"][0]["quantity"] = "0.00"

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("consumption_items", response.data)
        self.assertEqual(ConsumptionRecord.objects.count(), 0)

    def test_create_consumption_with_negative_quantity(self):
        """A negative quantity should be rejected."""
        self.payload["consumption_items"][0]["quantity"] = "-1.00"

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("consumption_items", response.data)
        self.assertEqual(ConsumptionRecord.objects.count(), 0)

    def test_create_consumption_with_future_date(self):
        """A future consumption date should be rejected."""
        self.payload["consumed_at"] = (
            timezone.now() + timedelta(days=1)
        ).isoformat()

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("consumed_at", response.data)
        self.assertEqual(ConsumptionRecord.objects.count(), 0)

    def test_create_consumption_with_nonexistent_food(self):
        """A nonexistent food should be rejected."""
        self.payload["consumption_items"][0]["food_id"] = str(uuid.uuid4())

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("consumption_items", response.data)
        self.assertEqual(ConsumptionRecord.objects.count(), 0)

    def test_create_consumption_without_items(self):
        """A consumption without items should be rejected."""
        self.payload["consumption_items"] = []

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ConsumptionRecord.objects.count(), 0)
