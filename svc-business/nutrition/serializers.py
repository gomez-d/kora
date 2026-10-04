from rest_framework import serializers
from .models import NutritionalProfile, Food


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


class FoodSearializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = [
            "id",
            "name",
            "calories",
            "protein",
            "carbohydrates",
            "fat",
            "fiber",
            "sugar",
            "sodium",
        ]

        def validate_name(self, value):
            if not value.strip():
                raise serializers.ValidationError(
                    "Name cannot be empty."
                )
            return value

        def validate_calories(self, value):
            if value < 0:
                raise serializers.ValidationError(
                    "Calories cannot be negative."
                )
            return value

        def validate_protein(self, value):
            if value < 0:
                raise serializers.ValidationError(
                    "Protein cannot be negative."
                )
            return value

        def validate_carbohydrates(self, value):
            if value < 0:
                raise serializers.ValidationError(
                    "Carbohydrates cannot be negative."
                )
            return value

        def validate_fat(self, value):
            if value < 0:
                raise serializers.ValidationError(
                    "Fat cannot be negative."
                )
            return value

        def validation_fiber(self, value):
            if value < 0:
                raise serializers.ValidationError(
                    "Fiber cannot be negative."
                )
            return value

        def validation_sugar(self, value):
            if value < 0:
                raise serializers.ValidationError(
                    "Sugar cannot be negative."
                )
            return value

        def validation_Sodium(self, value):
            if value < 0:
                raise serializers.ValidationError(
                    "Sodium cannot be negative."
                )
