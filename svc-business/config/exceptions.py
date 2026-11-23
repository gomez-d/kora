
from rest_framework.exceptions import (
    ParseError,
    ValidationError,
)
from rest_framework.views import exception_handler


def kora_exception_handler(exc, context):
    """
    Standardize validation, authentication, and authorization
    error responses across the Kora Business service.
    """

    response = exception_handler(exc, context)

    # Let DRF handle exceptions without an API response.
    if response is None:
        return None

    if isinstance(exc, ValidationError):
        response.data = {
            "success": False,
            "code": "validation_error",
            "message": "Invalid request data.",
            "errors": response.data,
        }
        return response

    if isinstance(exc, ParseError):
        response.data = {
            "success": False,
            "code": "invalid_json",
            "message": "Invalid JSON payload.",
        }
        return response

    if response.status_code == 401:
        response.data = {
            "success": False,
            "code": "unauthorized",
            "message": "Authentication credentials are missing or invalid.",
        }

    elif response.status_code == 403:
        response.data = {
            "success": False,
            "code": "forbidden",
            "message": "You do not have permission to perform this operation.",
        }

    return response
