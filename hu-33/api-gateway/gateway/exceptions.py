from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and response.status_code in (401, 403):
        message = "Authentication credentials were not provided or are invalid."
        if response.status_code == 403:
            message = "You do not have permission to perform this action."

        response.data = {
            "success": False,
            "message": message,
        }

    return response