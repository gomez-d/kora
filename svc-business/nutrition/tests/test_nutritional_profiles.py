from datetime import date, timedelta
from unittest.mock import patch
from uuid import uuid4

from rest_framework import status
from rest_framework.test import APITestCase

from nutrition.models import NutritionalProfile
from nutrition.tests.utils import authenticate_test_client


class NutritionalProfileTests(APITestCase):
    def setUp(self):
        self.url = "/api/nutritional-profiles/"
        self.user_id = uuid4()
        self.other_user_id = uuid4()

        authenticate_test_client(
            self.client,
            user_id=self.user_id,
            permissions=[
                "nutritional_profiles.create_self",
                "nutritional_profiles.read_self",
            ],
        )

        self.payload = {
            "user_id": str(self.user_id),
            "date_of_birth": "1995-05-15",
            "sex": "MALE",
            "weight": "75.50",
            "height": "1.75",
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
        self.assertIn("user_id", response.data["errors"])

    def test_list_profiles_rejects_invalid_user_id(self):
        response = self.client.get(
            self.url,
            {"user_id": "invalid-uuid"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
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
        self.assertIn("date_of_birth", response.data["errors"])
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
        self.assertIn("date_of_birth", response.data["errors"])
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
        self.assertIn("weight", response.data["errors"])
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
        self.assertIn("height", response.data["errors"])
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
        self.assertIn("user_id", response.data["errors"])
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
            status.HTTP_403_FORBIDDEN,
        )
        mock_user_exists.assert_not_called()
