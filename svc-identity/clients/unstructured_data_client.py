import logging
import requests

from django.conf import settings
from requests.exceptions import (
    ConnectionError,
    RequestException,
    Timeout
)

logger = logging.getLogger(__name__)

# Base URL of the unstructured data microservice.
UNSTRUCTURED_DATA_SERVICE_URL = settings.UNSTRUCTURED_DATA_SERVICE_URL

def log_audit_failure(error, status_code=None):
    """
    Log audit delivery failures without exposing sensitive data.
    """

    logger.warning(
        "Identity audit event delivery failed. "
        "Error: %s. HTTP status: %s.",
        error,
        status_code,
    )


def send_identity_event(user_id, event, level='INFO', data=None, metadata=None):
    """
    Send an identity event to the unstructured data microservice.

    The event is sent through the API established for communication
    between identity and unstructured data services.
    """

    url = (
        f'{UNSTRUCTURED_DATA_SERVICE_URL}'
        '/api/documents/identity-events/'
    )

    payload = {
        'user_id': str(user_id) if user_id is not None else None,
        'event': event,
        'level': level,
        'data': data or {},
        'metadata': metadata or {},
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                'Authorization': f'Bearer {settings.UNSTRUCTURED_DATA_SERVICE_TOKEN}'
            },
            timeout=2,
        )

        # Handle HTTP error responses returned by the remote service.
        if not response.ok:
            log_audit_failure(
                error='invalid_response',
                status_code=response.status_code,
            )

            return {
                'success': False,
                'error': 'invalid_response',
                'status_code': response.status_code,
            }

        try:
            response_data = response.json()
        except ValueError:
            log_audit_failure('invalid_json_response')

            return {
                'success': False,
                'error': 'invalid_json_response',
            }

        return {
            'success': True,
            'status_code': response.status_code,
            'data': response_data,
        }

    except Timeout:
        log_audit_failure('timeout')

        return {
            'success': False,
            'error': 'timeout',
        }

    except ConnectionError:
        log_audit_failure('service_unavailable')

        return {
            'success': False,
            'error': 'service_unavailable',
        }

    except RequestException:
        log_audit_failure('communication_error')

        return {
            'success': False,
            'error': 'communication_error',
        }
