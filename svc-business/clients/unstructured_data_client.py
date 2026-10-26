import os
import requests

# Base URL of the unstructured data microservice.
UNSTRUCTURED_DATA_SERVICE_URL = os.getenv(
    'UNSTRUCTURED_DATA_SERVICE_URL'
)

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

    response = requests.post(
        url,
        json=payload,
        timeout=5,
    )

    return response

def get_documents(document_type):
    """
    Retrieve all documents from a supported MongoDB collection.
    """

    url = (
        f'{UNSTRUCTURED_DATA_SERVICE_URL}'
        f'/api/documents/{document_type}'
    )

    response = requests.get(
        url,
        timeout=5,
    )

    return response

def get_document(document_type, document_id):
    """
    Retrieve a specific MongoDB document by its document ID.
    """

    url = (
        f'{UNSTRUCTURED_DATA_SERVICE_URL}'
        f'/api/documents/{document_type}/{document_id}'
    )

    response = requests.get(
        url,
        timeout=5,
    )

    return response