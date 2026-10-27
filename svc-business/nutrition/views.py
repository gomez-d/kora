from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

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

from datetime import date
from uuid import UUID


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "ok",
            "service": "business"
        })


class NutritionalProfileListCreateView(generics.ListCreateAPIView):
    queryset = NutritionalProfile.objects.all()
    serializer_class = NutritionalProfileSerializer



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

        return Response(
            serializer.errors,
            status=400
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
        serializer = ConsumptionRecordSerializer(data=request.data)

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
