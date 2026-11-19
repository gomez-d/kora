from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from django.db import IntegrityError

from nutrition.models import (
    NutritionalProfile,
    Food,
    FoodCategory,
    ConsumptionRecord
)
from nutrition.serializers import (
    NutritionalProfileSerializer,
    FoodCategorySerializer,
    FoodSerializer,
    FoodReadSerializer,
    ConsumptionRecordSerializer,
    ConsumptionHistorySerializer
)
from nutrition.pagination import ConsumptionPagination
from clients.identity_client import user_exists

from datetime import date
from uuid import UUID


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "ok",
            "service": "business"
        })


class NutritionalProfileView(APIView):
    def get(self, request):
        user_id = request.query_params.get("user_id")

        if not user_id:
            raise ValidationError({
                "user_id": "The user_id query parameter is required."
            })

        try:
            user_uuid = UUID(user_id)
        except (ValueError, TypeError):
            raise ValidationError({
                "user_id": "The user_id must be a valid UUID.",
            })

        profiles = NutritionalProfile.objects.filter(user_id=user_uuid)
        serializer = NutritionalProfileSerializer(profiles, many=True)

        return Response(
            serializer.data,
            status=200
        )

    def post(self, request):
        user_id = request.data.get("user_id")

        if not user_id:
            raise ValidationError({
                "user_id": "The user_id field is required.",
            })

        try:
            user_uuid = UUID(str(user_id))
        except (ValueError, TypeError, AttributeError):
            raise ValidationError({
                "user_id": "The user_id field must be a valid UUID.",
            })

        exists = user_exists(user_uuid)

        if exists is False:
            raise ValidationError({
                "user_id": "The specified user does not exist.",
            })

        if exists is None:
            return Response(
                {"detail": "Unable to verify the user with Identity service."},
                status=503
            )

        serializer = NutritionalProfileSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(user_id=user_uuid)

        return Response(
            serializer.data,
            status=201
        )


class FoodCategoryView(APIView):
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

class FoodView(APIView):
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

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=201
        )


class FoodDetailView(APIView):
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

        serializer.is_valid(raise_exception=True)
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

        serializer.is_valid(raise_exception=True)
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
    def get(self, request):
        consumptions = ConsumptionRecord.objects.prefetch_related(
            "consumption_items__food"
        )

        user_id = request.query_params.get("user_id")

        if not user_id:
            raise ValidationError({
                "user_id": "The user_id parameter is required.",
            })

        try:
            user_id = UUID(user_id)
        except ValueError:
            raise ValidationError({
                "user_id": "Invalid user_id format.",
            })

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
            raise ValidationError({
                "date": "Dates must use YYYY-MM-DD format.",
            })

        if start_date and end_date and start_date > end_date:
            raise ValidationError({
                "date_range": "start_date cannot be after end_date.",
            })

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
            raise ValidationError({
                "user_id": "The user_id field is required.",
            })

        try:
            user_uuid = UUID(str(user_id))
        except (ValueError, TypeError, AttributeError):
            raise ValidationError({
                "user_id": "The user_id field must be a valid UUID.",
            })

        exists = user_exists(user_uuid)

        if exists is False:
            raise ValidationError({
                "user_id": "The specified user does not exist.",
            })

        if exists is None:
            return Response(
                {"detail": "Unable to verify the user with Identity Service."},
                status=503
            )

        serializer = ConsumptionRecordSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(user_id=user_uuid)

        return Response(
            serializer.data,
            status=201
        )
