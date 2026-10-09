import uuid
from django.db import models

# Define NutritionalProfile choices
SEX_CHOICES = [
    ("MALE", "Hombre"),
    ("FEMALE", "Mujer")
]

ACTIVITY_LEVEL_CHOICES = [
    ("NONE", "Nula"),
    ("LOW", "Poco"),
    ("MODERATE", "Moderada"),
    ("HIGH", "Alta"),
    ("VERY_HIGH", "Muy alta")
]

NUTRITION_GOAL_CHOICES = [
    ("WEIGHT_LOSS", "Pérdida de peso"),
    ("WEIGHT_MAINTENANCE", "Mantenimiento de peso"),
    ("WEIGHT_GAIN", "Aumento de peso"),
    ("HEALTHY_EATING", "Alimentación saludable")
]

# Define Food choices
SERVING_UNIT_CHOICES = [
    ("G", "Gramos"),
    ("ML", "Mililitros"),
    ("UNIT", "Unidad")
]

# Define FoodNutrient choices
NUTRIENT_TYPE_CHOICES = [
    ("CALORIES", "Calorías"),
    ("PROTEIN", "Proteínas"),
    ("CARBOHYDRATES", "Carbohidratos"),
    ("FAT", "Grasas"),
    ("FIBER", "Fibra"),
    ("SUGAR", "Azúcares"),
    ("SODIUM", "Sodio")
]

NUTRIENT_UNIT_CHOICES = [
    ("G", "Gramos"),
    ("MG", "Miligramos"),
    ("KCAL", "Kilocalorías")
]


class NutritionalProfile(models.Model):
    user_id = models.UUIDField()
    age = models.PositiveSmallIntegerField()
    sex = models.CharField(
        max_length=10,
        choices=SEX_CHOICES
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    activity_level = models.CharField(
        max_length=10,
        choices=ACTIVITY_LEVEL_CHOICES
    )
    nutrition_goal = models.CharField(
        max_length=20,
        choices=NUTRITION_GOAL_CHOICES
    )


class FoodCategory(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)


class Food(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    category = models.ForeignKey(
        FoodCategory,
        on_delete=models.PROTECT,
        related_name="foods"
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    serving_size = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    serving_unit = models.CharField(
        max_length=20,
        choices=SERVING_UNIT_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FoodNutrient(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    food = models.ForeignKey(
        Food,
        on_delete=models.CASCADE,
        related_name="nutrients"
    )
    nutrient_type = models.CharField(
        max_length=20,
        choices=NUTRIENT_TYPE_CHOICES
    )
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    unit = models.CharField(
        max_length=10,
        choices=NUTRIENT_UNIT_CHOICES
    )
