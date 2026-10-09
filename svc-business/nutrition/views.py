from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NutritionalProfile
from .serializers import (
    NutritionalProfileSerializer,
    FoodCategorySerializer,
    FoodSerializer
)


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


class FoodCreateView(APIView):
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
