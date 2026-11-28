
import uuid
from datetime import datetime, timezone


AI_PROCESSING_REQUESTED = "ai.processing.requested"
AI_PROCESSING_COMPLETED = "ai.processing.completed"
AI_PROCESSING_FAILED = "ai.processing.failed"

AI_REQUESTS_STREAM = "ai:requests"
AI_RESULTS_STREAM = "ai:results"

EVENT_STREAMS = {
    AI_PROCESSING_REQUESTED: AI_REQUESTS_STREAM,
    AI_PROCESSING_COMPLETED: AI_RESULTS_STREAM,
    AI_PROCESSING_FAILED: AI_RESULTS_STREAM,
}


def generate_id():
    return str(uuid.uuid4())


def generate_timestamp():
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def validate_event(event):
    if not isinstance(event, dict):
        raise ValueError("Event must be a dictionary.")

    required_fields = {
        "event_id",
        "event_type",
        "timestamp",
        "data",
    }

    if not required_fields.issubset(event):
        raise ValueError("Event is missing required fields.")

    for field in ("event_id", "event_type", "timestamp"):
        if not isinstance(event[field], str) or not event[field].strip():
            raise ValueError(f"Invalid event field: {field}.")

    if event["event_type"] not in EVENT_STREAMS:
        raise ValueError("Unsupported event type.")

    try:
        datetime.fromisoformat(
            event["timestamp"].replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise ValueError("Invalid event timestamp.") from exc

    data = event["data"]

    if not isinstance(data, dict):
        raise ValueError("Event data must be a dictionary.")

    required_data = {"request_id", "operation"}

    if not required_data.issubset(data):
        raise ValueError("Event data is missing required fields.")

    for field in ("request_id", "operation"):
        if not isinstance(data[field], str) or not data[field].strip():
            raise ValueError(f"Invalid event data field: {field}.")

    if "user_id" in data:
        if not isinstance(data["user_id"], str) or not data["user_id"].strip():
            raise ValueError("Invalid user_id.")

    event_type = event["event_type"]

    if event_type == AI_PROCESSING_REQUESTED:
        if not isinstance(data.get("payload"), dict):
            raise ValueError("Processing request requires a payload.")

    elif event_type == AI_PROCESSING_COMPLETED:
        if data.get("status") != "completed":
            raise ValueError("Completed event requires completed status.")

        if not isinstance(data.get("result"), dict):
            raise ValueError("Completed event requires a result.")

    elif event_type == AI_PROCESSING_FAILED:
        if data.get("status") != "failed":
            raise ValueError("Failed event requires failed status.")

        if not isinstance(data.get("error"), dict):
            raise ValueError("Failed event requires error details.")

    return True


def build_ai_processing_request(
    user_id,
    operation,
    payload,
    request_id=None,
):
    event = {
        "event_id": generate_id(),
        "event_type": AI_PROCESSING_REQUESTED,
        "timestamp": generate_timestamp(),
        "data": {
            "request_id": request_id or generate_id(),
            "user_id": str(user_id),
            "operation": operation,
            "payload": payload,
        },
    }

    validate_event(event)

    return event
