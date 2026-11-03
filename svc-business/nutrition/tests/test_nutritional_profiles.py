from datetime import date, timedelta
from uuid import uuid4
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from nutrition.models import NutritionalProfile


class NutritionalProfileTests(APITestCase):
    def setUp(self):
        self.url = "/api/nutritional-profiles/"
        self.user_id = uuid4()
        self.other_user_id = uuid4()

        self.payload = {
            "user_id": str(self.user_id),
            "date_of_birth": "1995-05-15",
            "sex": "MALE",
            "weight": "75.50",
            "height": "175.00",
            "activity_level": "MODERATE",
        }

    @patch("nutrition.views.user_exists", return_value=True)
    def test_create_nutritional_profile(self, mock_user_exists):
        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["user_id"],
            str(self.user_id),
        )
        self.assertTrue(
            NutritionalProfile.objects.filter(
                user_id=self.user_id
            ).exists()
        )
        mock_user_exists.assert_called_once_with(self.user_id)

    def test_list_profiles_by_user_id(self):
        NutritionalProfile.objects.create(
            user_id=self.user_id,
            date_of_birth=date(1995, 5, 15),
            sex="MALE",
            weight="75.50",
            height="175.00",
            activity_level="MODERATE",
        )
        NutritionalProfile.objects.create(
            user_id=self.other_user_id,
            date_of_birth=date(1990, 8, 20),
            sex="FEMALE",
            weight="60.00",
            height="165.00",
            activity_level="LOW",
        )

        response = self.client.get(
            self.url,
            {"user_id": str(self.user_id)},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["user_id"],
            str(self.user_id),
        )

    def test_list_profiles_requires_user_id(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["detail"],
            "The user_id query parameter is required.",
        )

    def test_list_profiles_rejects_invalid_user_id(self):
        response = self.client.get(
            self.url,
            {"user_id": "invalid-uuid"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["detail"],
            "The user_id must be a valid UUID.",
        )

    @patch("nutrition.views.user_exists", return_value=True)
    def test_create_profile_rejects_future_date_of_birth(
        self,
        mock_user_exists,
    ):
        future_date = date.today() + timedelta(days=1)
        payload = {
            **self.payload,
            "date_of_birth": future_date.isoformat(),
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("date_of_birth", response.data)
        mock_user_exists.assert_called_once_with(self.user_id)

    @patch("nutrition.views.user_exists", return_value=True)
    def test_create_profile_rejects_invalid_age(
        self,
        mock_user_exists,
    ):
        payload = {
            **self.payload,
            "date_of_birth": date.today().isoformat(),
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("date_of_birth", response.data)
        mock_user_exists.assert_called_once_with(self.user_id)

    @patch("nutrition.views.user_exists", return_value=True)
    def test_create_profile_rejects_non_positive_weight(
        self,
        mock_user_exists,
    ):
        payload = {
            **self.payload,
            "weight": "0.00",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("weight", response.data)
        mock_user_exists.assert_called_once_with(self.user_id)

    @patch("nutrition.views.user_exists", return_value=True)
    def test_create_profile_rejects_non_positive_height(
        self,
        mock_user_exists,
    ):
        payload = {
            **self.payload,
            "height": "0.00",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("height", response.data)
        mock_user_exists.assert_called_once_with(self.user_id)

    @patch("nutrition.views.user_exists", return_value=True)
    def test_create_profile_with_existing_user(
        self,
        mock_user_exists,
    ):
        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        mock_user_exists.assert_called_once_with(self.user_id)

    @patch("nutrition.views.user_exists", return_value=False)
    def test_create_profile_rejects_non_existing_user(
        self,
        mock_user_exists,
    ):
        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            response.data["detail"],
            "The specified user does not exist.",
        )
        self.assertFalse(
            NutritionalProfile.objects.filter(
                user_id=self.user_id
            ).exists()
        )
        mock_user_exists.assert_called_once_with(self.user_id)

    @patch("nutrition.views.user_exists", return_value=None)
    def test_create_profile_handles_identity_unavailable(
        self,
        mock_user_exists,
    ):
        response = self.client.post(
            self.url,
            self.payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
        mock_user_exists.assert_called_once_with(self.user_id)
        self.assertFalse(
            NutritionalProfile.objects.filter(
                user_id=self.user_id
            ).exists()
        )

    @patch("nutrition.views.user_exists")
    def test_create_profile_rejects_invalid_user_id_without_identity_call(
        self,
        mock_user_exists,
    ):
        payload = {
            **self.payload,
            "user_id": "invalid-uuid",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        mock_user_exists.assert_not_called()
