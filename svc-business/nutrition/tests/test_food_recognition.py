import tempfile
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import jwt
import redis

from django.conf import settings
from django.test import override_settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from django.core.files.uploadedfile import SimpleUploadedFile


class FoodRecognitionTests(APITestCase):

    def setUp(self):
        self.user_id = str(uuid4())

        token_payload = {
            "user_id": self.user_id,
            "token_type": "access",
            "roles": ["USER"],
            "permissions": [
                "food_recognition.create_self",
            ],
        }

        token = jwt.encode(
            token_payload,
            settings.JWT_SIGNING_KEY,
            algorithm="HS256",
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        self.url = reverse("food-recognition")

        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.settings_override = override_settings(
            AI_IMAGES_DIR=Path(self.temp_dir.name)
        )
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

    def create_image(self, content_type="image/jpeg"):
        extension = (
            ".png" if content_type == "image/png"
            else ".webp" if content_type == "image/webp"
            else ".jpg"
        )

        return SimpleUploadedFile(
            f"test{extension}",
            b"fake-image-content",
            content_type=content_type,
        )

    def test_unauthenticated_request_returns_401(self):
        self.client.credentials()

        response = self.client.post(
            self.url,
            {},
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_without_permission_returns_403(self):
        token = jwt.encode(
            {
                "user_id": self.user_id,
                "token_type": "access",
                "roles": ["USER"],
                "permissions": [],
            },
            settings.JWT_SIGNING_KEY,
            algorithm="HS256",
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        response = self.client.post(
            self.url,
            {"image": self.create_image()},
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_missing_image_returns_400(self):
        response = self.client.post(
            self.url,
            {},
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_unsupported_image_type_returns_400(self):
        response = self.client.post(
            self.url,
            {
                "image": self.create_image("image/gif"),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    @patch("nutrition.recognition.publish_event")
    def test_image_is_stored_and_event_is_published(
        self,
        mock_publish,
    ):
        response = self.client.post(
            self.url,
            {
                "image": self.create_image(),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_202_ACCEPTED,
        )

        mock_publish.assert_called_once()

        event = mock_publish.call_args.args[0]

        self.assertEqual(
            event["event_type"],
            "ai.processing.requested",
        )

        self.assertEqual(
            event["data"]["operation"],
            "food_recognition",
        )

        image_reference = event["data"]["payload"]["image_reference"]

        filename = image_reference.split("/")[-1]

        self.assertTrue(
            (Path(self.temp_dir.name) / filename).exists()
        )

        self.assertEqual(
            response.data["request_id"],
            event["data"]["request_id"],
        )

    @patch(
        "nutrition.recognition.publish_event",
        side_effect=redis.ConnectionError("Redis unavailable"),
    )
    def test_redis_failure_deletes_temporary_image(
        self,
        mock_publish,
    ):
        response = self.client.post(
            self.url,
            {
                "image": self.create_image(),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

        self.assertEqual(
            list(Path(self.temp_dir.name).iterdir()),
            [],
        )
