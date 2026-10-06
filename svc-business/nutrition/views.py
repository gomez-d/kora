from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NutritionalProfile, Food
from .serializers import NutritionalProfileSerializer, FoodSearializer


class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "status": "ok",
            "service": "business"
        })


class NutritionalProfileListCreateView(generics.ListCreateAPIView):
    queryset = NutritionalProfile.objects.all()
    serializer_class = NutritionalProfileSerializer


class FoodCreateView(generics.CreateAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSearializer
