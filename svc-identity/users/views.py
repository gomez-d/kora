from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from users.serializers import UserRegistrationSerializer

class HealthCheckView(APIView):
    def get(self, request):
        return Response ({
            "status": "ok",
            "service": "identity"
        })

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "User registered successfully.",
                    "data": UserRegistrationSerializer(user).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "message": "Validation error.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )