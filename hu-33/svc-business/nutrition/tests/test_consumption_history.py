
import uuid
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from nutrition.models import (
    ConsumptionRecord,
    ConsumptionItem,
    Food,
    FoodCategory,
)


class ConsumptionHistoryTests(APITestCase):
    def setUp(self):
        self.url = "/api/consumptions/"
        self.user_id = uuid.uuid4()
        self.other_user_id = uuid.uuid4()

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

        now = timezone.now()
        self.old_record = self.create_consumption(
            self.user_id,
            now - timedelta(days=3),
            "Consumo antiguo",
            with_item=False,
        )
        self.middle_record = self.create_consumption(
            self.user_id,
            now - timedelta(days=2),
            "Consumo intermedio",
            with_item=True,
        )
        self.new_record = self.create_consumption(
            self.user_id,
            now - timedelta(days=1),
            "Consumo reciente",
            with_item=True,
        )
        self.other_user_record = self.create_consumption(
            self.other_user_id,
            now - timedelta(days=1),
            "Consumo de otro usuario",
            with_item=False,
        )

    def create_consumption(
        self, user_id, consumed_at, notes, with_item=False
    ):
        record = ConsumptionRecord.objects.create(
            user_id=user_id,
            consumed_at=consumed_at,
            notes=notes,
        )

        if with_item:
            ConsumptionItem.objects.create(
                consumption=record,
                food=self.food,
                quantity="1.00",
                calories="52.00",
                protein="0.26",
                carbohydrates="13.81",
                fat="0.17",
                fiber="2.40",
                sugar="10.39",
                sodium="1.00",
            )

        return record

    def get_history(self, **params):
        return self.client.get(
            self.url,
            {"user_id": str(self.user_id), **params},
            format="json",
        )

    def test_get_history_returns_only_requested_user_records(self):
        response = self.get_history()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

        returned_ids = {
            item["id"] for item in response.data["results"]
        }
        expected_ids = {
            str(self.old_record.id),
            str(self.middle_record.id),
            str(self.new_record.id),
        }

        self.assertSetEqual(returned_ids, expected_ids)
        self.assertNotIn(
            str(self.other_user_record.id),
            returned_ids,
        )

    def test_history_requires_user_id(self):
        response = self.client.get(self.url, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["detail"],
            "The user_id parameter is required.",
        )

    def test_history_rejects_invalid_user_id(self):
        response = self.client.get(
            self.url,
            {"user_id": "usuario_invalido"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["detail"],
            "Invalid user_id format.",
        )

    def test_history_returns_empty_results_for_user_without_records(self):
        response = self.client.get(
            self.url,
            {"user_id": str(uuid.uuid4())},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_filter_by_start_date(self):
        start_date = (
            self.middle_record.consumed_at.date()
        ).isoformat()

        response = self.get_history(start_date=start_date)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        returned_ids = {
            item["id"] for item in response.data["results"]
        }
        self.assertNotIn(str(self.old_record.id), returned_ids)

    def test_filter_by_end_date(self):
        end_date = (
            self.old_record.consumed_at.date()
        ).isoformat()

        response = self.get_history(end_date=end_date)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.old_record.id),
        )

    def test_filter_by_date_range(self):
        start_date = self.middle_record.consumed_at.date().isoformat()
        end_date = self.new_record.consumed_at.date().isoformat()

        response = self.get_history(
            start_date=start_date,
            end_date=end_date,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_reject_invalid_date_format(self):
        response = self.get_history(start_date="21-10-2026")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["detail"],
            "Dates must use YYYY-MM-DD format.",
        )

    def test_reject_start_date_after_end_date(self):
        response = self.get_history(
            start_date="2026-10-23",
            end_date="2026-10-22",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["detail"],
            "start_date cannot be after end_date.",
        )

    def test_ordering_oldest_first(self):
        response = self.get_history(ordering="consumed_at")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [
            item["id"] for item in response.data["results"]
        ]
        self.assertEqual(
            returned_ids,
            [
                str(self.old_record.id),
                str(self.middle_record.id),
                str(self.new_record.id),
            ],
        )

    def test_ordering_newest_first_by_default(self):
        response = self.get_history()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [
            item["id"] for item in response.data["results"]
        ]
        self.assertEqual(
            returned_ids,
            [
                str(self.new_record.id),
                str(self.middle_record.id),
                str(self.old_record.id),
            ],
        )

    def test_invalid_ordering_uses_default(self):
        response = self.get_history(ordering="fecha_invalida")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [
            item["id"] for item in response.data["results"]
        ]
        self.assertEqual(
            returned_ids,
            [
                str(self.new_record.id),
                str(self.middle_record.id),
                str(self.old_record.id),
            ],
        )

    def test_pagination_returns_requested_page(self):
        response = self.get_history(page=1, page_size=2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

        second_page = self.get_history(page=2, page_size=2)

        self.assertEqual(second_page.status_code, status.HTTP_200_OK)
        self.assertEqual(len(second_page.data["results"]), 1)
        self.assertIsNone(second_page.data["next"])
        self.assertIsNotNone(second_page.data["previous"])

    def test_history_serializes_consumption_items(self):
        response = self.get_history()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results_by_id = {
            item["id"]: item for item in response.data["results"]
        }
        record = results_by_id[str(self.new_record.id)]

        self.assertIn("consumption_items", record)
        self.assertEqual(len(record["consumption_items"]), 1)

        item = record["consumption_items"][0]
        self.assertEqual(item["food"], "MANZANA")
        self.assertEqual(item["serving_unit"], "G")
        self.assertEqual(item["quantity"], "1.00")
        self.assertIn("calories", item)
        self.assertIn("protein", item)

    def test_history_rejects_page_out_of_range(self):
        response = self.get_history(page=3, page_size=2)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
