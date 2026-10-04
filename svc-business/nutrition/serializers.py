from rest_framework import serializers
from .models import NutritionalProfile


class NutritionalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionalProfile
        fields = [
            "id",
            "user_id",
            "age",
            "sex",
            "weight",
            "height",
            "activity_level",
            "nutrition_goal"
        ]

    def validate_age(self, value):
        if value < 1 or value > 120:
            raise serializers.ValidationError(
                "Age must be between 1 and 120 years."
            )
        return value

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Weight must be greater than 0."
            )
        return value

    def validate_height(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Height must be greater than 0."
            )
        return value
