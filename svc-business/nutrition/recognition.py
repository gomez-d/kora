import logging
from pathlib import Path
from uuid import uuid4

import redis

from django.conf import settings

from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import HasSelfBusinessPermission
from messaging.contracts import build_ai_processing_request
from messaging.publisher import publish_event


logger = logging.getLogger(__name__)


class FoodRecognitionView(APIView):
    """
    Receives a food image and publishes an asynchronous
    recognition request through Redis Streams.
    """

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [
        IsAuthenticated,
        HasSelfBusinessPermission,
    ]

    required_permissions = {
        "POST": "food_recognition.create_self",
    }

    allowed_content_types = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    def post(self, request):
        image = request.FILES.get("image")

        if image is None:
            return Response(
                {
                    "success": False,
                    "code": "image_required",
                    "message": "An image file is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        extension = self.allowed_content_types.get(image.content_type)

        if extension is None:
            return Response(
                {
                    "success": False,
                    "code": "unsupported_image_type",
                    "message": "Only JPEG, PNG and WebP images are supported.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        filename = f"{uuid4().hex}{extension}"
        image_path = Path(settings.AI_IMAGES_DIR) / filename

        try:
            with image_path.open("wb") as destination:
                for chunk in image.chunks():
                    destination.write(chunk)

        except OSError:
            logger.exception("Unable to store food recognition image.")

            return Response(
                {
                    "success": False,
                    "code": "image_storage_failed",
                    "message": "Unable to store the uploaded image.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        image_reference = f"storage://images/{filename}"

        event = build_ai_processing_request(
            user_id=request.user.user_id,
            operation="food_recognition",
            payload={
                "image_reference": image_reference,
            },
        )

        try:
            publish_event(event)

        except redis.RedisError:
            logger.exception(
                "Unable to publish food recognition request."
            )

            image_path.unlink(missing_ok=True)

            return Response(
                {
                    "success": False,
                    "code": "event_publication_failed",
                    "message": "Unable to submit the image for processing.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "request_id": event["data"]["request_id"],
                "status": "processing",
                "message": "Food recognition request accepted.",
            },
            status=status.HTTP_202_ACCEPTED,
        )
