from rest_framework.views import exception_handler
from clients.unstructured_data_client import send_identity_event


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
        request = context.get("request")
        view = context.get("view")

        user = getattr(request, "user", None)
        user_id = (
            user.id
            if user and user.is_authenticated
            else None
        )

        send_identity_event(
            user_id=user_id,
            event="access_denied",
            level="WARNING",
            metadata={
                "source": "exception_handler",
                "method": request.method if request else None,
                "view": view.__class__.__name__ if view else None
            }
        )

        response.data = {
            "success": False,
            "code": "forbidden",
            "message": "You do not have permission to perform this operation.",
        }

    return response