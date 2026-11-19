from rest_framework.exceptions import (
    NotAuthenticated,
    ParseError,
    PermissionDenied,
    ValidationError,
)
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Return standardized API error responses without exposing internal details.
    """

    response = exception_handler(exc, context)

    if response is None:
        return response

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

    if isinstance(exc, NotAuthenticated):
        response.data = {
            "success": False,
            "code": "unauthorized",
            "message": (
                "Authentication credentials are missing or invalid."
            ),
        }

        return response

    if isinstance(exc, PermissionDenied):
        response.data = {
            "success": False,
            "code": "forbidden",
            "message": (
                "You do not have permission to perform this operation."
            ),
        }

        return response

    return response