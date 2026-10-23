from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.utils import timezone

from .models import (
    NutritionalProfile,
    Food,
    FoodCategory,
    FoodNutrient,
    ConsumptionRecord,
    ConsumptionItem
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
        allow_blank=True,
        validators=[
            UniqueValidator(
                queryset=FoodCategory.objects.all(),
                lookup="iexact",
                message="A category with this name already exists."
            )
        ]
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
                "The category name cannot be empty."
            )

        return value.strip().upper()

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "The description of a category cannot be empty."
            )

        return value.strip().upper()


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
        allow_blank=True,
        validators=[
            UniqueValidator(
                queryset=Food.objects.all(),
                lookup="iexact",
                message="There is already a food product with this name."
            )
        ]
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

    def validate_nutrients(self, value):
        nutrient_types = [
            nutrient["nutrient_type"]
            for nutrient in value
        ]

        if len(nutrient_types) != len(set(nutrient_types)):
            raise serializers.ValidationError(
                "Repeating the type of nutrient in a food item is not permitted."
            )

        return value

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "El nombre del alimento no puede estar vacío."
            )

        return value.strip().upper()

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "The description cannot be empty."
            )

        return value.strip().upper()

    def validate_serving_size(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "The portion size must be greater than zero."
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


class FoodReadSerializer(serializers.ModelSerializer):
    category = FoodCategorySerializer(read_only=True)
    nutrients = FoodNutrientSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Food
        fields = [
            "id",
            "category",
            "name",
            "description",
            "serving_size",
            "serving_unit",
            "nutrients",
            "created_at",
            "updated_at"
        ]


class ConsumptionItemSerializer(serializers.ModelSerializer):
    food_id = serializers.PrimaryKeyRelatedField(
        source="food",
        queryset=Food.objects.all()
    )

    class Meta:
        model = ConsumptionItem
        fields = [
            "id",
            "food_id",
            "quantity",
            "calories",
            "protein",
            "carbohydrates",
            "fat",
            "fiber",
            "sugar",
            "sodium"
        ]
        read_only_field = [
            "id"
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than zero."
            )

        return value


class ConsumptionRecordSerializer(serializers.ModelSerializer):
    consumption_items = ConsumptionItemSerializer(
        many=True,
        allow_empty=False
    )
    notes = serializers.CharField(
        allow_blank=True
    )

    class Meta:
        model = ConsumptionRecord
        fields = [
            "id",
            "user_id",
            "consumed_at",
            "notes",
            "consumption_items",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at"
        ]

    def validate_consumed_at(self, value):
        if value > timezone.now():
            raise serializers.ValidationError(
                "Consumption date and time cannot be in the future"
            )

        return value

    def validate_notes(self, value):
        return value.strip().upper()

    def create(self, validated_data):
        items_data = validated_data.pop("consumption_items")

        record = ConsumptionRecord.objects.create(**validated_data)

        for item_data in items_data:
            ConsumptionItem.objects.create(
                consumption=record,
                **item_data
            )

        return record
