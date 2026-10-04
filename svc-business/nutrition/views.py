from rest_framework import generics

from .models import NutritionalProfile, Food
from .serializers import NutritionalProfileSerializer, FoodSearializer


class NutritionalProfileListCreateView(generics.ListCreateAPIView):
    queryset = NutritionalProfile.objects.all()
    serializer_class = NutritionalProfileSerializer


class FoodCreateView(generics.CreateAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSearializer
