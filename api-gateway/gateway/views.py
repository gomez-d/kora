
import requests

from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.conf import settings
from gateway.clients.base import forward_request
from rest_framework import status
from gateway.permissions import IsAuthenticatedOrPublicRoute
from rest_framework.exceptions import APIException
from gateway.throttling import (
    LoginRateThrottle,
    RegistrationRateThrottle,
    RefreshRateThrottle,
    AuthenticatedUserRateThrottle,
    PasswordResetRequestRateThrottle,
    PasswordResetConfirmRateThrottle,
)


def build_forward_headers(request):
    """
    Forward only explicitly allowed headers.

    Authentication must come from the validated Bearer token.
    Client-provided identity headers are never forwarded.
    """

    headers = {}

    authorization = request.headers.get("Authorization")
    content_type = request.headers.get("Content-Type")

    if authorization:
        headers["Authorization"] = authorization

    if content_type:
        headers["Content-Type"] = content_type

    # Forward the client IP obtained from the trusted connection.
    client_ip = request.META.get("REMOTE_ADDR")

    if client_ip: 
        headers["X-Forwarded-For"] = client_ip

    return headers


class HealthCheckView(APIView):

    def get(self, request):
        return Response({
            "status": "ok",
            "service": "api_gateway"
        })


class BusinessProxyView(APIView):
    permission_classes = [IsAuthenticatedOrPublicRoute]

    def get_throttles(self):
        return [AuthenticatedUserRateThrottle()]

    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        # Convert Django's request into a DRF Request.
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers

        try:
            self.initial(request, *args, **kwargs)
        except APIException as exc:
            response = self.handle_exception(exc)
            return self.finalize_response(
                request, response, *args, **kwargs
            )

        path = kwargs["path"]

        url = f"{settings.BUSINESS_SERVICE_URL}/api/{path}/"
        method = request.method
        headers = build_forward_headers(request)
        params = request.query_params
        json = request.data

        # Forward the incoming request to Business.
        try:
            response = forward_request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json
            )

        except requests.RequestException:
            response = Response(
                {"error": "Business service is unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

            return self.finalize_response(
                request, response, *args, **kwargs
            )

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type=response.headers.get("Content-Type")
        )


class IdentityProxyView(APIView):
    permission_classes = [IsAuthenticatedOrPublicRoute]

    def get_throttles(self):
        path = self.kwargs.get("path", "").strip("/")

        if path == "users/login":
            throttle_classes = [LoginRateThrottle]

        elif path == "users/register":
            throttle_classes = [RegistrationRateThrottle]

        elif path == "users/token/refresh":
            throttle_classes = [RefreshRateThrottle]

        elif path == "users/password-reset":
            throttle_classes = [PasswordResetRequestRateThrottle]

        elif path == "users/password-reset/confirm":
            throttle_classes = [PasswordResetConfirmRateThrottle]

        else:
            throttle_classes = [AuthenticatedUserRateThrottle]

        return [throttle() for throttle in throttle_classes]

    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        # Convert Django's request into a DRF Request.
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers

        try:
            self.initial(request, *args, **kwargs)
        except APIException as exc:
            response = self.handle_exception(exc)
            return self.finalize_response(
                request, response, *args, **kwargs
            )

        path = kwargs["path"]

        url = f"{settings.IDENTITY_SERVICE_URL}/api/{path}/"
        method = request.method
        headers = build_forward_headers(request)
        params = request.query_params
        json = request.data

        # Forward the incoming request to Identity.
        try:
            response = forward_request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json
            )

        except requests.RequestException:
            response = Response(
                {"error": "Identity service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

            return self.finalize_response(
                request, response, *args, **kwargs
            )

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type=response.headers.get("Content-Type")
        )


class AIProxyView(APIView):
    permission_classes = [IsAuthenticatedOrPublicRoute]

    def get_throttles(self):
        return [AuthenticatedUserRateThrottle()]

    def dispatch(self, request, *args, **kwargs):

        # Handle multipart uploads before DRF parses the request body.
        if request.method == "POST":
            path = kwargs["path"].strip("/")
            content_type = request.headers.get("Content-Type", "")

            if content_type.startswith("multipart/form-data"):

                drf_request = self.initialize_request(
                    request, *args, **kwargs
                )

                self.request = drf_request
                self.headers = self.default_response_headers

                try:
                    self.initial(drf_request, *args, **kwargs)

                except APIException as exc:
                    response = self.handle_exception(exc)

                    return self.finalize_response(
                        drf_request,
                        response,
                        *args,
                        **kwargs
                    )

                if path.startswith("vision/"):
                    url = f"{settings.AI_SERVICE_URL}/{path}"
                else:
                    url = f"{settings.AI_SERVICE_URL}/ai/{path}"

                headers = build_forward_headers(drf_request)

                try:
                    response = forward_request(
                        method="POST",
                        url=url,
                        headers=headers,
                        params=request.GET,
                        data=request.body,
                    )

                except requests.RequestException as exc:
                    print(
                        f"AI proxy connection error: "
                        f"{type(exc).__name__}: {exc}"
                    )

                    return HttpResponse(
                        '{"error":"AI service is unavailable"}',
                        status=503,
                        content_type="application/json",
                    )

                return HttpResponse(
                    response.content,
                    status=response.status_code,
                    content_type=response.headers.get(
                        "Content-Type",
                        "application/json",
                    ),
                )

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        path = kwargs["path"].strip("/")
        url = f"{settings.AI_SERVICE_URL}/ai/{path}"

        try:
            response = forward_request(
                method="POST",
                url=url,
                headers=build_forward_headers(request),
                params=request.query_params,
                json=request.data,
            )

        except requests.RequestException as exc:
            print(
                f"AI proxy connection error: "
                f"{type(exc).__name__}: {exc}"
            )

            return Response(
                {"error": "AI service is unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type=response.headers.get(
                "Content-Type",
                "application/json",
            ),
        )
