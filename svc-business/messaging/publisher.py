
import json
import logging

import redis

from messaging.contracts import EVENT_STREAMS, validate_event


logger = logging.getLogger(__name__)


def get_redis_client():
    from clients.redis_client import redis_client
    return redis_client


def publish_event(event):
    try:
        validate_event(event)

    except (TypeError, ValueError) as exc:
        logger.warning(
            "Event validation failed: error_type=%s",
            type(exc).__name__,
        )
        raise

    event_type = event["event_type"]
    stream_name = EVENT_STREAMS[event_type]

    try:
        message = json.dumps(
            event,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    except (TypeError, ValueError) as exc:
        logger.error(
            "Event serialization failed: "
            "event_id=%s event_type=%s error_type=%s",
            event["event_id"],
            event_type,
            type(exc).__name__,
        )
        raise

    try:
        redis_client = get_redis_client()

        message_id = redis_client.xadd(
            stream_name,
            {"message": message},
        )

        logger.info(
            "Event published successfully: "
            "event_id=%s event_type=%s stream=%s",
            event["event_id"],
            event_type,
            stream_name,
        )

        return message_id

    except redis.RedisError as exc:
        logger.error(
            "Redis event publication failed: "
            "event_id=%s event_type=%s stream=%s error_type=%s",
            event["event_id"],
            event_type,
            stream_name,
            type(exc).__name__,
        )
        raise
