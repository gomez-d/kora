from rest_framework import generics

from .models import NutritionalProfile
from .serializers import NutritionalProfileSerializer


class NutritionalProfileListCreateView(generics.ListCreateAPIView):
    queryset = NutritionalProfile.objects.all()
    serializer_class = NutritionalProfileSerializer
