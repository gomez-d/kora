import requests

from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.conf import settings
from gateway.clients.base import forward_request


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

        url = f"{settings.BUSINESS_SERVICE_URL}/api/{path}"
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

        url = f"{settings.IDENTITY_SERVICE_URL}/api/{path}"
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
