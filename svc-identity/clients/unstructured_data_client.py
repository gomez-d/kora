import os
import requests
from requests.exceptions import (
    ConnectionError,
    RequestException,
    Timeout
)

# Base URL of the unstructured data microservice.
UNSTRUCTURED_DATA_SERVICE_URL = os.getenv(
    'UNSTRUCTURED_DATA_SERVICE_URL'
)

def send_identity_event(user_id, event, level='INFO', data=None, metadata=None,):
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
        'user_id': str(user_id),
        'event': event,
        'level': level,
        'data': data or {},
        'metadata': metadata or {},
    }

    try:
        response = requests.post(
            url, json=payload,
            timeout=5,
        )

        # Handle HTTP error responses returned by the remote service.
        if not response.ok:
            return {
                'success': False,
                'error': 'invalid_response',
                'status_code': response.status_code,
            }

        try:
            response_data = response.json()
        except ValueError:
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
        return {
            'success': False,
            'error': 'timeout',
        }

    except ConnectionError:
        return {
            'success': False,
            'error': 'service_unavailable',
        }

    except RequestException:
        return {
            'success': False,
            'error': 'communication_error',
        }