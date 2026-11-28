
from datetime import datetime

from django.test import SimpleTestCase

from messaging.contracts import (
    AI_PROCESSING_REQUESTED,
    AI_PROCESSING_COMPLETED,
    AI_PROCESSING_FAILED,
    AI_REQUESTS_STREAM,
    AI_RESULTS_STREAM,
    EVENT_STREAMS,
    build_ai_processing_request,
    generate_id,
    generate_timestamp,
    validate_event,
)


class EventContractTests(SimpleTestCase):

    def test_generate_id_returns_unique_identifiers(self):
        """Generated identifiers should be unique."""
        first_id = generate_id()
        second_id = generate_id()

        self.assertNotEqual(first_id, second_id)

    def test_generate_timestamp_returns_valid_utc_timestamp(self):
        """Generated timestamps should use UTC."""
        timestamp = generate_timestamp()

        self.assertTrue(timestamp.endswith("Z"))
        self.assertIsInstance(
            datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
            datetime,
        )

    def test_event_types_are_mapped_to_correct_streams(self):
        """Each event type should use its corresponding Redis stream."""
        self.assertEqual(
            EVENT_STREAMS[AI_PROCESSING_REQUESTED],
            AI_REQUESTS_STREAM,
        )
        self.assertEqual(
            EVENT_STREAMS[AI_PROCESSING_COMPLETED],
            AI_RESULTS_STREAM,
        )
        self.assertEqual(
            EVENT_STREAMS[AI_PROCESSING_FAILED],
            AI_RESULTS_STREAM,
        )

    def test_build_ai_processing_request_creates_valid_event(self):
        """A processing request should follow the event contract."""
        payload = {
            "image_reference": "storage://images/test.jpg",
        }

        event = build_ai_processing_request(
            user_id="user-test-001",
            operation="food_recognition",
            payload=payload,
        )

        self.assertEqual(
            event["event_type"],
            AI_PROCESSING_REQUESTED,
        )
        self.assertEqual(
            event["data"]["user_id"],
            "user-test-001",
        )
        self.assertEqual(
            event["data"]["operation"],
            "food_recognition",
        )
        self.assertEqual(event["data"]["payload"], payload)
        self.assertTrue(validate_event(event))

    def test_build_ai_processing_request_preserves_request_id(self):
        """A supplied request ID should be preserved."""
        request_id = "request-test-001"

        event = build_ai_processing_request(
            user_id="user-test-001",
            operation="food_recognition",
            payload={"image_reference": "storage://images/test.jpg"},
            request_id=request_id,
        )

        self.assertEqual(event["data"]["request_id"], request_id)

    def test_validate_event_rejects_non_dictionary(self):
        """Events that are not dictionaries should be rejected."""
        with self.assertRaises(ValueError):
            validate_event("invalid-event")

    def test_validate_event_rejects_missing_fields(self):
        """Events missing required fields should be rejected."""
        event = {
            "event_id": "event-test-001",
            "event_type": AI_PROCESSING_REQUESTED,
        }

        with self.assertRaises(ValueError):
            validate_event(event)

    def test_validate_event_rejects_unsupported_event_type(self):
        """Unsupported event types should be rejected."""
        event = {
            "event_id": "event-test-001",
            "event_type": "invalid.event",
            "timestamp": "2026-11-27T02:00:00Z",
            "data": {
                "request_id": "request-test-001",
                "operation": "food_recognition",
                "payload": {},
            },
        }

        with self.assertRaises(ValueError):
            validate_event(event)

    def test_validate_event_rejects_invalid_timestamp(self):
        """Events with invalid timestamps should be rejected."""
        event = {
            "event_id": "event-test-001",
            "event_type": AI_PROCESSING_REQUESTED,
            "timestamp": "invalid-timestamp",
            "data": {
                "request_id": "request-test-001",
                "operation": "food_recognition",
                "payload": {},
            },
        }

        with self.assertRaises(ValueError):
            validate_event(event)

    def test_validate_event_rejects_missing_request_data(self):
        """Processing requests must include a dictionary payload."""
        event = {
            "event_id": "event-test-001",
            "event_type": AI_PROCESSING_REQUESTED,
            "timestamp": "2026-11-27T02:00:00Z",
            "data": {
                "request_id": "request-test-001",
                "operation": "food_recognition",
            },
        }

        with self.assertRaises(ValueError):
            validate_event(event)
