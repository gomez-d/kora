
import json
from unittest.mock import patch

import redis
from django.test import SimpleTestCase

from messaging.contracts import (
    AI_PROCESSING_REQUESTED,
    AI_REQUESTS_STREAM,
    build_ai_processing_request,
)
from messaging.publisher import publish_event


class EventPublisherTests(SimpleTestCase):

    def setUp(self):
        self.event = build_ai_processing_request(
            user_id="user-test-001",
            operation="food_recognition",
            payload={
                "image_reference": "storage://images/test.jpg",
            },
        )

    @patch("messaging.publisher.get_redis_client")
    def test_publish_event_successfully(self, mock_get_client):
        """A valid event should be published successfully."""
        mock_client = mock_get_client.return_value
        mock_client.xadd.return_value = "1234567890-0"

        message_id = publish_event(self.event)

        self.assertEqual(message_id, "1234567890-0")
        mock_client.xadd.assert_called_once()

        args, kwargs = mock_client.xadd.call_args

        self.assertEqual(args[0], AI_REQUESTS_STREAM)
        self.assertIn("message", args[1])

        published_event = json.loads(args[1]["message"])

        self.assertEqual(
            published_event["event_type"],
            AI_PROCESSING_REQUESTED,
        )
        self.assertEqual(
            published_event["data"]["operation"],
            "food_recognition",
        )

    @patch("messaging.publisher.get_redis_client")
    def test_publish_event_uses_correct_stream(self, mock_get_client):
        """Processing requests should be published to ai:requests."""
        mock_client = mock_get_client.return_value
        mock_client.xadd.return_value = "1234567890-0"

        publish_event(self.event)

        mock_client.xadd.assert_called_once_with(
            AI_REQUESTS_STREAM,
            {"message": json.dumps(
                self.event,
                ensure_ascii=False,
                separators=(",", ":"),
            )},
        )

    @patch("messaging.publisher.get_redis_client")
    def test_publish_event_rejects_invalid_event(self, mock_get_client):
        """Invalid events should not be published."""
        invalid_event = {
            "event_id": "event-test-001",
            "event_type": "invalid.event",
            "timestamp": "2026-11-27T02:00:00Z",
            "data": {},
        }

        with self.assertRaises(ValueError):
            publish_event(invalid_event)

        mock_get_client.assert_not_called()

    @patch("messaging.publisher.get_redis_client")
    def test_publish_event_handles_serialization_error(
        self,
        mock_get_client,
    ):
        """Serialization errors should be propagated."""
        invalid_event = self.event.copy()
        invalid_event["data"] = self.event["data"].copy()
        invalid_event["data"]["invalid_value"] = object()

        with self.assertRaises(TypeError):
            publish_event(invalid_event)

        mock_get_client.assert_not_called()

    @patch("messaging.publisher.get_redis_client")
    def test_publish_event_handles_redis_connection_error(
        self,
        mock_get_client,
    ):
        """Redis connection errors should be logged and propagated."""
        mock_client = mock_get_client.return_value
        mock_client.xadd.side_effect = redis.ConnectionError(
            "Simulated Redis disconnection"
        )

        with self.assertRaises(redis.ConnectionError):
            publish_event(self.event)

        mock_client.xadd.assert_called_once()
