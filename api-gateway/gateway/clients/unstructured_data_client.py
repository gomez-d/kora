import logging

import requests
from django.conf import settings
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


def send_gateway_event(event, level="INFO", metadata=None):
    """
    Send a Gateway audit event to Unstructured Data.

    Audit failures must not interrupt the original request.
    """
    url = (
        f"{settings.UNSTRUCTURED_DATA_SERVICE_URL.rstrip('/')}"
        "/api/documents/identity-events/"
    )

    payload = {
        "user_id": None,
        "event": event,
        "level": level,
        "data": {},
        "metadata": metadata or {},
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": (
                    f"Bearer {settings.UNSTRUCTURED_DATA_SERVICE_TOKEN}"
                )
            },
            timeout=2,
        )

        if not response.ok:
            logger.warning(
                "Gateway audit event delivery failed. HTTP status: %s.",
                response.status_code,
            )
            return False

        return True

    except RequestException as exc:
        logger.warning(
            "Gateway audit event delivery failed. Error: %s.",
            type(exc).__name__,
        )
        return False
