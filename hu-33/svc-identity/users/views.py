from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    UserTokenRefreshSerializer
)
from .models import User
from rbac.utils import (
    get_user_role_names,
    get_user_permission_names,
)
from rbac.permissions import (
    HasKoraPermission,
    HasSelfOrKoraPermission
)
from clients.unstructured_data_client import send_identity_event


class HealthCheckView(APIView):
    """
    Expose the Identity service health status without requiring
    authentication.
    """

    # Health checks must remain publicly accessible for service
    # availability monitoring.
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "status": "ok",
            "service": "identity"
        })


class UserView(APIView):
    """
    Allow authorized administrators to retrieve active users.
    """

    # Listing users is an administrative operation.
    permission_classes = [
        IsAuthenticated,
        HasKoraPermission
    ]

    required_permissions = {
        "GET": "users.read_any"
    }

    def get(self, request):
        users = User.objects.filter(is_active=True)

        serializer = UserDetailSerializer(users, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class UserRegistrationView(APIView):
    """
    Register new Kora users without requiring an existing session.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "User registered successfully.",
                    "data": UserDetailSerializer(user).data,
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
    """
    Protect user detail operations according to ownership
    and effective RBAC permissions.
    """

    permission_classes = [
        IsAuthenticated,
        HasSelfOrKoraPermission
    ]

    # Permissions used when the URL user_id belongs to
    # the authenticated identity.
    self_permissions = {
        "GET": "users.read_self",
        "DELETE": "users.deactivate_self",
    }

    # Permissions used when the requested user_id belongs
    # to another user.
    any_permissions = {
        "GET": "users.read_any",
        "DELETE": "users.deactivate_any",
    }

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserDetailSerializer(user)

        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def delete(self, request, user_id):
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

        user.is_active = False
        user.save(update_fields=["is_active"])

        return Response(
            {
                "success": True,
                "message": "User deactivated successfully."
            }
        )


class UserUpdateView(APIView):
    """
    Allow authenticated users to update only their own
    user information.
    """

    permission_classes = [
        IsAuthenticated,
        HasSelfOrKoraPermission
    ]

    self_permissions = {
        "PUT": "users.update_self",
        "PATCH": "users.update_self",
    }

    # No permission currently allows modifying another user's
    # personal information through this endpoint.
    any_permissions = {}

    def put(self, request, user_id):
        return self.update_user(request, user_id, partial=False)

    def patch(self, request, user_id):
        return self.update_user(request, user_id, partial=True)

    def update_user(self, request, user_id, partial):
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

        serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=partial
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "User updated successfully.",
                    "data": UserDetailSerializer(user).data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "message": "Validation error.",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class UserLoginView(APIView):
    """
    Authenticate users and issue their signed identity context.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation error.",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            request=request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"]
        )

        if user is None:
            send_identity_event(
                user_id=None,
                event="login_failed",
                level="WARNING",
                metadata={
                    "source": "user_login"
                }
            )

            return Response(
                {
                    "success": False,
                    "message": "Invalid credentials."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        refresh = RefreshToken.for_user(user)

        # Add the current user roles to the signed identity context.
        refresh["roles"] = get_user_role_names(user)

        # Add the user's effective permissions to the signed identity context.
        refresh["permissions"] = get_user_permission_names(user)

        return Response(
            {
                "success": True,
                "message": "Credentials verified successfully.",
                "data": {
                    "user_id": str(user.id),
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            },
            status=status.HTTP_200_OK
        )


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {
                    "success": False,
                    "message": "Refresh token is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)

            user_id = token.get(api_settings.USER_ID_CLAIM)

            if str(user_id) != str(request.user.id):
                send_identity_event(
                    user_id=request.user.id,
                    event="invalid_token_attempt",
                    level="WARNING",
                    metadata={
                        "source": "user_logout",
                        "reason": "user_mismatch"
                    }
                )

                return Response(
                    {
                        "success": False,
                        "message": "Invalid refresh token."
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )

            token.blacklist()

            send_identity_event(
                user_id=request.user.id,
                event="token_revoked",
                level="INFO",
                metadata={
                    "source": "user_logout"
                }
            )

            return Response(
                {
                    "success": True,
                    "message": "Logout successful."
                },
                status=status.HTTP_200_OK
            )

        except TokenError:
            send_identity_event(
                user_id=request.user.id,
                event="invalid_token_attempt",
                level="WARNING",
                metadata={
                    "source": "user_logout",
                    "reason": "invalid_or_expired"
                }
            )

            return Response(
                {
                    "success": False,
                    "message": "Invalid or expired refresh token."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserTokenRefreshView(TokenRefreshView):
    """
    Refresh access tokens using the user's current identity context.
    """

    serializer_class = UserTokenRefreshSerializer