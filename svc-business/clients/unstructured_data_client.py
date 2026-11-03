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

def _handle_response(response):
    """
    Convert an HTTP response into a structured result.
    """

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
        'data': response_data
    }

def create_document(document_type, document):
    """
    Send a flexible document to the unstructured data microservice.
    """

    url = (
        f'{UNSTRUCTURED_DATA_SERVICE_URL}'
        '/api/documents/'
    )

    payload = {
        'document_type': document_type,
        'document': document
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=5,
        )

        return _handle_response(response)
    except Timeout:
        return {
            'success': False,
            'error': 'timeout'
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

def get_documents(document_type):
    """
    Retrieve all documents from a supported MongoDB collection.
    """

    url = (
        f'{UNSTRUCTURED_DATA_SERVICE_URL}'
        f'/api/documents/{document_type}'
    )

    try: 
        response = requests.get(
            url,
            timeout=5,
        )

        return _handle_response(response)

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

def get_document(document_type, document_id):
    """
    Retrieve a specific MongoDB document by its document ID.
    """

    url = (
        f'{UNSTRUCTURED_DATA_SERVICE_URL}'
        f'/api/documents/{document_type}/{document_id}'
    )

    try:
        response = requests.get(
            url,
            timeout=5,
        )

        return _handle_response(response)

    except Timeout:
        return {
            'success': False,
            'error': 'timeout',
        }

    except ConnectionError:
        return {
            'success': False,
            'error':'service_unavailable',
        }

    except RequestException:
        return {
            'success': False,
            'error': 'communication_error',
        }