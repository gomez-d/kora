from rest_framework import serializers

from .models import (
    NutritionalProfile,
    Food,
    FoodCategory,
    FoodNutrient
)


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


class FoodCategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        allow_blank=True
    )

    description = serializers.CharField(
        allow_blank=True
    )

    class Meta:
        model = FoodCategory
        fields = [
            "id",
            "name",
            "description"
        ]
        read_only_fields = [
            "id"
        ]

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "El nombre de la categoría no puede estar vacío."
            )

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "La descripción de una categoría no puede estar vacía."
            )

        return value.strip()


class FoodNutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodNutrient
        fields = [
            "id",
            "nutrient_type",
            "amount",
            "unit"
        ]
        read_only_fields = [
            "id"
        ]

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "La cantidad del nutriente no puede ser negativa."
            )

        return value


class FoodSerializer(serializers.ModelSerializer):
    # Expose the foreign key as category_id in the API
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=FoodCategory.objects.all()
    )

    name = serializers.CharField(
        allow_blank=True
    )

    description = serializers.CharField(
        allow_blank=True
    )

    nutrients = FoodNutrientSerializer(
        many=True,
        allow_empty=False
    )

    class Meta:
        model = Food
        fields = [
            "id",
            "category_id",
            "name",
            "description",
            "serving_size",
            "serving_unit",
            "nutrients",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at"
        ]

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "El nombre del alimento no puede estar vacío."
            )

        return value.strip()

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "La descripción no puede estar vacía."
            )

        return value.strip()

    def validate_serving_size(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El tamaño de la porción debe ser mayor que cero."
            )

        return value

    def create(self, validated_data):
        # Extract nutrients because they belong to FoodNutrient, not Food.
        nutrients_data = validated_data.pop("nutrients")

        # Create the food before creating its related nutrinets
        food = Food.objects.create(**validated_data)

        # Associate each nutrient with the newly created food
        for nutrient_data in nutrients_data:
            FoodNutrient.objects.create(
                food=food,
                **nutrient_data
            )

        return food
