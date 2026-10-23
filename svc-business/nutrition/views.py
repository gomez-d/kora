from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import IntegrityError

from .models import NutritionalProfile, Food
from .serializers import (
    NutritionalProfileSerializer,
    FoodCategorySerializer,
    FoodSerializer,
    FoodReadSerializer
)
from .pagination import FoodPagination


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "ok",
            "service": "business"
        })


class NutritionalProfileListCreateView(generics.ListCreateAPIView):
    queryset = NutritionalProfile.objects.all()
    serializer_class = NutritionalProfileSerializer


class FoodCategoryCreateView(APIView):
    def post(self, request):
        serializer = FoodCategorySerializer(
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

        paginator = FoodPagination()
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
