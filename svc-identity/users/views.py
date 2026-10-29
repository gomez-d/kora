from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import UserRegistrationSerializer
from .models import User


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
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


class UserDetailView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "success": True,
                "data": {
                    "user_id": str(user.id)
                }
            },
            status=status.HTTP_200_OK
        )
