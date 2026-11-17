from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from django.db import IntegrityError

from .models import (
    NutritionalProfile,
    Food,
    FoodCategory,
    ConsumptionRecord
)
from .serializers import (
    NutritionalProfileSerializer,
    FoodCategorySerializer,
    FoodSerializer,
    FoodReadSerializer,
    ConsumptionRecordSerializer,
    ConsumptionHistorySerializer
)
from .pagination import ConsumptionPagination
from .clients.identity import user_exists

from .permissions import (
    HasBusinessPermission,
    HasSelfBusinessPermission,
    HasOwnedBusinessPermission
)

from datetime import date
from uuid import UUID


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "ok",
            "service": "business"
        })


class NutritionalProfileView(APIView):
    permission_classes = [
        IsAuthenticated,
        HasSelfBusinessPermission
    ]

    required_permissions = {
        "GET": "nutritional_profiles.read_self",
        "POST": "nutritional_profiles.create_self",
    }

    def get(self, request):
        user_id = request.query_params.get("user_id")

        if not user_id:
            return Response(
                {"detail": "The user_id query parameter is required."},
                status=400
            )

        try:
            user_uuid = UUID(user_id)
        except (ValueError, TypeError):
            return Response(
                {"detail": "The user_id must be a valid UUID."},
                status=400
            )

        profiles = NutritionalProfile.objects.filter(user_id=user_uuid)
        serializer = NutritionalProfileSerializer(profiles, many=True)

        return Response(
            serializer.data,
            status=200
        )

    def post(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"detail": "The user_id field is required."},
                status=400
            )

        try:
            user_uuid = UUID(str(user_id))
        except (ValueError, TypeError, AttributeError):
            return Response(
                {"detail": "The user_id field must be a valid UUID."},
                status=400
            )

        exists = user_exists(user_uuid)

        if exists is False:
            return Response(
                {"detail": "The specified user does not exist."},
                status=400
            )

        if exists is None:
            return Response(
                {"detail": "Unable to verify the user with Identity service."},
                status=503
            )

        serializer = NutritionalProfileSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user_id=user_uuid)
            return Response(
                serializer.data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )

class NutritionalProfileDetailView(APIView):
    """
    Manage an existing nutritional profile while enforcing
    permission and resource ownership rules.
    """

    # Require authentication and validate the permission associated
    # with the requested operation.
    permission_classes = [
        IsAuthenticated,
        HasOwnedBusinessPermission
    ]

    # Updating a nutritional profile is allowed only through the
    # self-scoped update permission.
    required_permissions = {
        "PATCH": "nutritional_profiles.update_self",
    }

    def patch(self, request, profile_id):
        """
        Partially update an existing nutritional profile only when
        the authenticated identity owns the stored resource.
        """

        # Retrieve the profile using its own resource identifier.
        # Ownership is not determined from data supplied by the client.
        try:
            profile = NutritionalProfile.objects.get(id=profile_id)
        except NutritionalProfile.DoesNotExist:
            return Response(
                {"detail": "Nutritional profile not found."},
                status=404
            )

        # Execute the object-level permission check.
        # HasOwnedBusinessPermission compares profile.user_id stored
        # in PostgreSQL against the trusted user_id from the JWT.
        self.check_object_permissions(
            request,
            profile
        )

        # The owner of the resource must remain immutable.
        # A client must not be able to transfer a nutritional profile
        # to another user by changing user_id through PATCH.
        if "user_id" in request.data:
            return Response(
                {
                    "detail": (
                        "The user_id field cannot be modified."
                    )
                },
                status=400
            )

        # Perform a partial update after authentication,
        # permission validation and ownership validation succeed.
        serializer = NutritionalProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=200
            )

        return Response(
            serializer.errors,
            status=400
        )

class FoodCategoryView(APIView):
    permission_classes = [
        IsAuthenticated, 
        HasBusinessPermission
    ]

    required_permissions = {
        "GET": "food_categories.read",
        "POST": "food_categories.create",
    }

    def get(self, request):
        categories = FoodCategory.objects.all().order_by("name")
        serializer = FoodCategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FoodCategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )


class FoodView(APIView):

    # Require a valid authenticated identity before checking
    # the permissions associated with food catalog operations.
    permission_classes = [
        IsAuthenticated,
        HasBusinessPermission
    ]

    # Define the permission required for each supported HTTP method.
    # Reading the catalog is available to authorized users,
    # while creating foods is restricted to administrative permissions.
    required_permissions = {
        "GET": "foods.read",
        "POST": "foods.create",
    }

    def get(self, request):
        foods = Food.objects.select_related(
            "category"
        ).prefetch_related(
            "nutrients"
        )

        search = request.query_params.get("search")
        category_id = request.query_params.get("category_id")

        if search:
            foods = foods.filter(name__icontains=search)

        if category_id:
            foods = foods.filter(category_id=category_id)

        ordering = request.query_params.get("ordering", "name")

        allowed_orderings = {
            "name",
            "-name",
            "created_at",
            "-created_at"
        }

        if ordering not in allowed_orderings:
            ordering = "name"

        foods = foods.order_by(ordering)

        paginator = ConsumptionPagination()
        page = paginator.paginate_queryset(foods, request, view=self)

        serializer = FoodReadSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = FoodSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )


class FoodDetailView(APIView):

    # Require an authenticated identity before evaluating
    # permissions for individual food resources.
    permission_classes = [
        IsAuthenticated,
        HasBusinessPermission
    ]

    # Associate each HTTP operation with its corresponding
    # RBAC permission.
    required_permissions = {
        "GET": "foods.read",
        "PUT": "foods.update",
        "PATCH": "foods.update",
        "DELETE": "foods.delete",
    }

    def get(self, request, food_id):
        try:
            food = Food.objects.select_related(
                "category").prefetch_related("nutrients").get(id=food_id)
        except Food.DoesNotExist:
            return Response(
                {"detail": "Food not found."},
                status=404
            )

        serializer = FoodReadSerializer(food)
        return Response(serializer.data)

    def put(self, request, food_id):
        try:
            food = Food.objects.get(id=food_id)
        except Food.DoesNotExist:
            return Response(
                {"detail": "Food not found."},
                status=404
            )

        serializer = FoodSerializer(
            food,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            updated_food = Food.objects.select_related(
                "category"
            ).prefetch_related(
                "nutrients"
            ).get(id=food_id)

            response_serializer = FoodReadSerializer(updated_food)

            return Response(
                response_serializer.data,
                status=200
            )

        return Response(
            serializer.errors,
            status=400
        )

    def patch(self, request, food_id):
        try:
            food = Food.objects.get(id=food_id)
        except Food.DoesNotExist:
            return Response(
                {"detail": "Food not found."},
                status=404
            )

        serializer = FoodSerializer(
            food,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            updated_food = Food.objects.select_related(
                "category"
            ).prefetch_related(
                "nutrients"
            ).get(id=food_id)

            response_serializer = FoodReadSerializer(updated_food)

            return Response(
                response_serializer.data,
                status=200
            )

        return Response(
            serializer.errors,
            status=400
        )

    def delete(self, request, food_id):
        try:
            food = Food.objects.get(id=food_id)
        except Food.DoesNotExist:
            return Response(
                {"detail": "Food not found."},
                status=404
            )

        try:
            food.delete()
        except IntegrityError:
            return Response(
                {
                    "detail": (
                        "Food cannot be deleted because "
                        "it is referenced by consumption records."
                    )
                },
                status=409
            )

        return Response(status=204)


class ConsumptionRecordView(APIView):

    # Require a valid authenticated identity before evaluating
    # any business authorization rule.
    permission_classes = [
        IsAuthenticated,
        HasSelfBusinessPermission
    ]

    # Define the specific permission required for each HTTP method.
    #
    # GET:
    # The authenticated user may only read their own consumption history.
    #
    # POST:
    # The authenticated user may only create consumption records
    # associated with their own identity.
    required_permissions = {
        "GET": "consumptions.read_self",
        "POST": "consumptions.create_self",
    }

    def get(self, request):
        consumptions = ConsumptionRecord.objects.prefetch_related(
            "consumption_items__food"
        )

        user_id = request.query_params.get("user_id")

        if not user_id:
            return Response(
                {"detail": "The user_id parameter is required."},
                status=400
            )

        try:
            user_id = UUID(user_id)
        except ValueError:
            return Response(
                {"detail": "Invalid user_id format."},
                status=400
            )

        consumptions = consumptions.filter(user_id=user_id)

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        try:
            if start_date:
                start_date = date.fromisoformat(start_date)
                consumptions = consumptions.filter(
                    consumed_at__date__gte=start_date
                )

            if end_date:
                end_date = date.fromisoformat(end_date)
                consumptions = consumptions.filter(
                    consumed_at__date__lte=end_date
                )
        except ValueError:
            return Response(
                {"detail": "Dates must use YYYY-MM-DD format."},
                status=400
            )

        if start_date and end_date and start_date > end_date:
            return Response(
                {"detail": "start_date cannot be after end_date."},
                status=400
            )

        ordering = request.query_params.get(
            "ordering",
            "-consumed_at"
        )

        allowed_orderings = {
            "consumed_at",
            "-consumed_at"
        }

        if ordering not in allowed_orderings:
            ordering = "-consumed_at"

        consumptions = consumptions.order_by(ordering)

        paginator = ConsumptionPagination()
        page = paginator.paginate_queryset(
            consumptions,
            request,
            view=self
        )

        serializer = ConsumptionHistorySerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"detail": "The user_id field is required."},
                status=400
            )

        try:
            user_uuid = UUID(str(user_id))
        except (ValueError, TypeError, AttributeError):
            return Response(
                {"detail": "The user_id field must be a valid UUID."},
                status=400
            )

        exists = user_exists(user_uuid)

        if exists is False:
            return Response(
                {"detail": "The specified user does not exist."},
                status=400
            )

        if exists is None:
            return Response(
                {"detail": "Unable to verify the user with Identity Service."},
                status=503
            )

        serializer = ConsumptionRecordSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user_id=user_uuid)

            return Response(
                serializer.data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )

class ConsumptionRecordDetailView(APIView):
    """
    Manage an existing consumption record while enforcing
    permission and resource ownership rules.
    """

    # Require authentication and verify the permission associated
    # with the requested operation.
    permission_classes = [
        IsAuthenticated,
        HasOwnedBusinessPermission
    ]

    # A user may update only consumption records that belong
    # to their own authenticated identity.
    required_permissions = {
        "PATCH": "consumptions.update_self",
    }

    def patch(self, request, consumption_id):
        """
        Partially update an existing consumption record only when
        the authenticated identity owns the stored resource.
        """

        # Retrieve the consumption record using its resource identifier.
        # Ownership is determined from the persisted resource and not
        # from a user_id supplied by the client.
        try:
            consumption = ConsumptionRecord.objects.get(
                id=consumption_id
            )
        except ConsumptionRecord.DoesNotExist:
            return Response(
                {"detail": "Consumption record not found."},
                status=404
            )

        # Execute the object-level permission check.
        # HasOwnedBusinessPermission compares consumption.user_id
        # stored in PostgreSQL with the trusted user_id from the JWT.
        self.check_object_permissions(
            request,
            consumption
        )

        # Resource ownership must remain immutable.
        # A client cannot transfer a consumption record to another user.
        if "user_id" in request.data:
            return Response(
                {
                    "detail": (
                        "The user_id field cannot be modified."
                    )
                },
                status=400
            )

        # Perform a partial update only after authentication,
        # permission validation and ownership validation succeed.
        serializer = ConsumptionRecordSerializer(
            consumption,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=200
            )

        return Response(
            serializer.errors,
            status=400
        )