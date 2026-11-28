from unittest.mock import patch
from uuid import uuid4

import jwt
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from nutrition.models import (
    ConsumptionRecord,
    Food,
    FoodCategory,
    NutritionalProfile,
)


class BusinessRbacAuthorizationTests(APITestCase):
    """
    Authorization tests for HU-029 RBAC behavior
    in the Business service.
    """

    def setUp(self):
        """
        Create isolated business resources and identities
        required by the authorization scenarios.
        """

        self.user_a_id = str(uuid4())
        self.user_b_id = str(uuid4())
        self.admin_id = str(uuid4())

        self.category = FoodCategory.objects.create(
            name="TEST CATEGORY"
        )

        self.food = Food.objects.create(
            category=self.category,
            name="TEST FOOD",
            description="Food used for RBAC authorization tests.",
            serving_size=100,
            serving_unit="G",
        )

        self.profile_a = NutritionalProfile.objects.create(
            user_id=self.user_a_id,
            date_of_birth="2000-01-01",
            sex="FEMALE",
            weight=60.00,
            height=165.00,
            activity_level="MODERATE",
        )

        self.profile_b = NutritionalProfile.objects.create(
            user_id=self.user_b_id,
            date_of_birth="1998-05-15",
            sex="MALE",
            weight=75.00,
            height=178.00,
            activity_level="MODERATE",
        )

        self.consumption_a = ConsumptionRecord.objects.create(
            user_id=self.user_a_id,
            consumed_at=timezone.now(),
            notes="USER A CONSUMPTION",
        )

        self.consumption_b = ConsumptionRecord.objects.create(
            user_id=self.user_b_id,
            consumed_at=timezone.now(),
            notes="USER B CONSUMPTION",
        )

    def generate_token(
        self,
        user_id,
        roles,
        permissions,
    ):
        """
        Generate a signed JWT containing the identity context
        expected by KoraJWTAuthentication.
        """

        payload = {
            "user_id": str(user_id),
            "token_type": "access",
            "roles": roles,
            "permissions": permissions,
        }

        return jwt.encode(
            payload,
            settings.JWT_SIGNING_KEY,
            algorithm="HS256",
        )

    def authenticate(
        self,
        user_id,
        roles,
        permissions,
    ):
        """
        Configure the API client with a signed Bearer token.
        """

        token = self.generate_token(
            user_id,
            roles,
            permissions,
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

    def test_admin_can_create_food(self):
        """
        Verify that an administrator with foods.create can
        execute an administrative catalog operation.
        """

        self.authenticate(
            self.admin_id,
            ["ADMIN"],
            ["foods.create"],
        )

        payload = {
            "category_id": str(self.category.id),
            "name": "ADMIN TEST FOOD",
            "description": "Created by an authorized administrator.",
            "serving_size": 100,
            "serving_unit": "G",
            "nutrients": [
                {
                    "nutrient_type": "CALORIES",
                    "amount": 100,
                    "unit": "KCAL",
                },
                {
                    "nutrient_type": "PROTEIN",
                    "amount": 10,
                    "unit": "G",
                },
                {
                    "nutrient_type": "CARBOHYDRATES",
                    "amount": 20,
                    "unit": "G",
                },
                {
                    "nutrient_type": "FAT",
                    "amount": 5,
                    "unit": "G",
                },
                {
                    "nutrient_type": "FIBER",
                    "amount": 3,
                    "unit": "G",
                },
                {
                    "nutrient_type": "SUGAR",
                    "amount": 4,
                    "unit": "G",
                },
                {
                    "nutrient_type": "SODIUM",
                    "amount": 50,
                    "unit": "MG",
                },
            ],
        }

        response = self.client.post(
            reverse("foods"),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_regular_user_cannot_create_food(self):
        """
        Verify that a regular user cannot execute
        an administrative food operation.
        """

        self.authenticate(
            self.user_a_id,
            ["USER"],
            ["foods.read"],
        )

        response = self.client.post(
            reverse("foods"),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_regular_user_can_read_own_profile(self):
        """
        Verify that a user can access their own
        nutritional profile.
        """

        self.authenticate(
            self.user_a_id,
            ["USER"],
            ["nutritional_profiles.read_self"],
        )

        response = self.client.get(
            reverse("nutritional-profile-list-create"),
            {
                "user_id": self.user_a_id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_regular_user_cannot_read_another_profile(self):
        """
        Verify that a user cannot access another user's
        nutritional profile by changing the user identifier.
        """

        self.authenticate(
            self.user_a_id,
            ["USER"],
            ["nutritional_profiles.read_self"],
        )

        response = self.client.get(
            reverse("nutritional-profile-list-create"),
            {
                "user_id": self.user_b_id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_regular_user_can_update_own_profile(self):
        """
        Verify that a user can modify their own
        persisted nutritional profile.
        """

        self.authenticate(
            self.user_a_id,
            ["USER"],
            ["nutritional_profiles.update_self"],
        )

        response = self.client.patch(
            reverse(
                "nutritional-profile-detail",
                kwargs={
                    "profile_id": self.profile_a.id,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_regular_user_cannot_update_another_profile(self):
        """
        Verify that ownership validation prevents a user from
        modifying another user's nutritional profile.
        """

        self.authenticate(
            self.user_a_id,
            ["USER"],
            ["nutritional_profiles.update_self"],
        )

        response = self.client.patch(
            reverse(
                "nutritional-profile-detail",
                kwargs={
                    "profile_id": self.profile_b.id,
                },
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_regular_user_can_read_own_consumptions(self):
        """
        Verify that a user can access their own
        consumption history.
        """

        self.authenticate(
            self.user_a_id,
            ["USER"],
            ["consumptions.read_self"],
        )

        response = self.client.get(
            reverse("consumption-create"),
            {
                "user_id": self.user_a_id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_regular_user_cannot_read_another_users_consumptions(self):
        """
        Verify that a user cannot access another user's
        consumption history.
        """

        self.authenticate(
            self.user_a_id,
            ["USER"],
            ["consumptions.read_self"],
        )

        response = self.client.get(
            reverse("consumption-create"),
            {
                "user_id": self.user_b_id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_regular_user_cannot_update_another_consumption(self):
        """
        Verify that a user cannot modify another user's
        persisted consumption record.
        """

        self.authenticate(
            self.user_a_id,
            ["USER"],
            ["consumptions.update_self"],
        )

        response = self.client.patch(
            reverse(
                "consumption-detail",
                kwargs={
                    "consumption_id": self.consumption_b.id,
                },
            ),
            {
                "notes": "UNAUTHORIZED UPDATE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_request_returns_401(self):
        """
        Verify that protected Business endpoints reject
        unauthenticated requests with HTTP 401.
        """

        response = self.client.get(
            reverse("foods")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertEqual(
            response.data["code"],
            "unauthorized",
        )
