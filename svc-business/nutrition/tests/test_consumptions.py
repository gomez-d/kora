
from datetime import timedelta
import uuid
from decimal import Decimal

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from nutrition.models import (
    ConsumptionRecord,
    ConsumptionItem,
    Food,
    FoodCategory,
    FoodNutrient,
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

        self.nutrients = [
            {
                "nutrient_type": "CALORIES",
                "amount": "52.00",
                "unit": "KCAL",
            },
            {
                "nutrient_type": "PROTEIN",
                "amount": "0.26",
                "unit": "G",
            },
            {
                "nutrient_type": "CARBOHYDRATES",
                "amount": "13.81",
                "unit": "G",
            },
            {
                "nutrient_type": "FAT",
                "amount": "0.17",
                "unit": "G",
            },
            {
                "nutrient_type": "FIBER",
                "amount": "2.40",
                "unit": "G",
            },
            {
                "nutrient_type": "SUGAR",
                "amount": "10.39",
                "unit": "G",
            },
            {
                "nutrient_type": "SODIUM",
                "amount": "1.00",
                "unit": "MG",
            },
        ]

        for nutrient_data in self.nutrients:
            FoodNutrient.objects.create(
                food=self.food,
                **nutrient_data,
            )

        self.url = "/api/consumptions/"

        self.payload = {
            "user_id": str(uuid.uuid4()),
            "consumed_at": timezone.now().isoformat(),
            "notes": "Consumo de prueba",
            "consumption_items": [
                {
                    "food_id": str(self.food.id),
                    "quantity": "150.00",
                }
            ],
        }

    def test_create_consumption_with_one_food(self):
        """A valid consumption with one food should be created."""
        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
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

        for nutrient_data in self.nutrients:
            FoodNutrient.objects.create(
                food=second_food,
                **nutrient_data,
            )

        second_item = {
            "food_id": str(second_food.id),
            "quantity": "100.00",
        }
        self.payload["consumption_items"].append(second_item)

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(ConsumptionRecord.objects.count(), 1)
        self.assertEqual(ConsumptionItem.objects.count(), 2)

    def test_calculate_nutritional_values_automatically(self):
        """Nutritional values should be calculated from quantity."""
        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        item = ConsumptionItem.objects.get()

        self.assertEqual(item.quantity, Decimal("150.00"))
        self.assertEqual(item.calories, Decimal("78.00"))
        self.assertEqual(item.protein, Decimal("0.39"))
        self.assertEqual(item.carbohydrates, Decimal("20.72"))
        self.assertEqual(item.fat, Decimal("0.26"))
        self.assertEqual(item.fiber, Decimal("3.60"))
        self.assertEqual(item.sugar, Decimal("15.59"))
        self.assertEqual(item.sodium, Decimal("1.50"))

    def test_client_cannot_override_nutritional_values(self):
        """Client-supplied nutritional values should be ignored."""
        self.payload["consumption_items"][0].update({
            "calories": "999.00",
            "protein": "999.00",
            "carbohydrates": "999.00",
            "fat": "999.00",
            "fiber": "999.00",
            "sugar": "999.00",
            "sodium": "999.00",
        })

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        item = ConsumptionItem.objects.get()
        self.assertEqual(item.calories, Decimal("78.00"))
        self.assertEqual(item.protein, Decimal("0.39"))

    def test_missing_nutrient_rejects_consumption(self):
        """Missing nutrients should prevent an incomplete consumption."""
        FoodNutrient.objects.filter(
            food=self.food,
            nutrient_type="SODIUM",
        ).delete()

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(ConsumptionRecord.objects.count(), 0)
        self.assertEqual(ConsumptionItem.objects.count(), 0)

    def test_invalid_nutrient_unit_rejects_consumption(self):
        """Nutrients with incorrect units should be rejected."""
        FoodNutrient.objects.filter(
            food=self.food,
            nutrient_type="SODIUM",
        ).update(unit="G")

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(ConsumptionRecord.objects.count(), 0)
        self.assertEqual(ConsumptionItem.objects.count(), 0)

    def test_create_consumption_with_zero_quantity(self):
        """A zero quantity should be rejected."""
        self.payload["consumption_items"][0]["quantity"] = "0.00"

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("consumption_items", response.data)
        self.assertEqual(ConsumptionRecord.objects.count(), 0)

    def test_create_consumption_with_negative_quantity(self):
        """A negative quantity should be rejected."""
        self.payload["consumption_items"][0]["quantity"] = "-1.00"

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
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

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("consumed_at", response.data)
        self.assertEqual(ConsumptionRecord.objects.count(), 0)

    def test_create_consumption_with_nonexistent_food(self):
        """A nonexistent food should be rejected."""
        self.payload["consumption_items"][0]["food_id"] = str(
            uuid.uuid4()
        )

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("consumption_items", response.data)
        self.assertEqual(ConsumptionRecord.objects.count(), 0)

    def test_create_consumption_without_items(self):
        """A consumption without items should be rejected."""
        self.payload["consumption_items"] = []

        response = self.client.post(
            self.url, self.payload, format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(ConsumptionRecord.objects.count(), 0)
