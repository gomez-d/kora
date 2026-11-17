from rest_framework.views import exception_handler


def kora_exception_handler(exc, context):
    """
    Standardize authentication and authorization error responses
    across the Kora Identity service.
    """

    response = exception_handler(exc, context)

    # Let DRF handle exceptions that do not produce an API response.
    if response is None:
        return None

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