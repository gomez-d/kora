import os
import requests

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

    response = requests.post(url, json=payload, timeout=5,)

    return response