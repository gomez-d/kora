import requests

from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.conf import settings
from gateway.clients.base import forward_request
from rest_framework import status


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "ok",
            "service": "api_gateway"
        })


class BusinessProxyView(APIView):
    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        # Convert Django's request into a DRF Request to access parsed API data
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request

        # Run DRF authentication, permissions, and throttling
        self.initial(request, *args, **kwargs)

        path = kwargs["path"]

        url = f"{settings.BUSINESS_SERVICE_URL}/api/{path}/"
        method = request.method
        headers = {
            "Authorization": request.headers.get("Authorization"),
            "Content-Type": request.headers.get("Content-Type")
        }
        params = request.query_params
        json = request.data

        # Forward the incoming request to the target microservice
        try:
            response = forward_request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json
            )
        except requests.RequestException:
            return Response(
                {"error": "Business service is unavailable"},
                status=503
            )

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type=response.headers.get("Content-Type")
        )


class IdentityProxyView(APIView):
    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        # Convert Django's request into a DRF Request to access parsed API data
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request

        # Run DRF authentication, permissions, and throttling
        self.initial(request, *args, **kwargs)

        path = kwargs["path"]

        url = f"{settings.IDENTITY_SERVICE_URL}/api/{path}/"
        method = request.method
        headers = {
            "Authorization": request.headers.get("Authorization"),
            "Content-Type": request.headers.get("Content-Type")
        }
        params = request.query_params
        json = request.data

        # Forward the incoming request to the target microservice
        try:
            response = forward_request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json
            )
        except requests.RequestException:
            return Response(
                {"error": "Identity service unavailable"},
                status=503
            )

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type=response.headers.get("Content-Type")
        )


class AIProxyView(APIView):
    def dispatch(self, request, *args, **kwargs):
        # Handle multipart uploads before DRF parses the request body.
        if request.method == "POST":
            path = kwargs["path"].strip("/")
            content_type = request.headers.get("Content-Type", "")

            if content_type.startswith("multipart/form-data"):
                if path.startswith("vision/"):
                    url = f"{settings.AI_SERVICE_URL}/{path}"
                else:
                    url = f"{settings.AI_SERVICE_URL}/ai/{path}"

                headers = {
                    "Content-Type": content_type,
                }

                authorization = request.headers.get("Authorization")
                if authorization:
                    headers["Authorization"] = authorization

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
                headers={
                    "Content-Type": "application/json",
                    **(
                        {"Authorization": request.headers["Authorization"]}
                        if "Authorization" in request.headers
                        else {}
                    ),
                },
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
