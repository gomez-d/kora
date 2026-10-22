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

NUTRITION_RESTRICTIONS_CHOICES = [
    ("ALLERGY", "Alergia"),
    ("UNAVAILABLE", "No disponible"),
    ("DISLIKE", "Disgusto")
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

"""
Nutritional models
"""


class NutritionalProfile(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user_id = models.UUIDField()
    date_of_birth = models.DateField()
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
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )


class Goal(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        max_length=20,
        choices=NUTRITION_GOAL_CHOICES
    )
    description = models.CharField(
        max_length=255
    )


class NutritionalGoal(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    profile = models.ForeignKey(
        NutritionalProfile,
        on_delete=models.CASCADE,
        related_name="nutritional_goals"
    )
    goal = models.ForeignKey(
        Goal,
        on_delete=models.PROTECT,
        related_name="nutritional_goals"
    )
    calories = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    protein = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    carbohydrates = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    fat = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    fiber = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    sugar = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    sodium = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )


class MedicalCondition(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    profile = models.ForeignKey(
        NutritionalProfile,
        on_delete=models.CASCADE,
        related_name="medical_conditions"
    )
    name = models.CharField(
        max_length=100
    )
    description = models.CharField(
        max_length=255
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("profile", "name"),
                name="unique_medical_condition_per_nutritional_profile"
            )
        ]


class DietaryPreference(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    profile = models.ForeignKey(
        NutritionalProfile,
        on_delete=models.CASCADE,
        related_name="dietary_preferences"
    )
    name = models.CharField(
        max_length=100
    )
    description = models.CharField(
        max_length=255
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("profile", "name"),
                name="unique_dietary_preference_per_profile"
            )
        ]


class RestrictionType(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    type = models.CharField(
        max_length=100,
        choices=NUTRITION_RESTRICTIONS_CHOICES
    )
    description = models.CharField(
        max_length=255
    )


class Restriction(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    profile = models.ForeignKey(
        NutritionalProfile,
        on_delete=models.CASCADE,
        related_name="restrictions"
    )
    restriction = models.ForeignKey(
        RestrictionType,
        on_delete=models.PROTECT,
        related_name="restrictions"
    )
    name = models.CharField(
        max_length=100
    )
    description = models.CharField(
        max_length=255
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("profile", "name"),
                name="unique_restriction_per_nutritional_profile"
            )
        ]


"""
Food models
"""


class FoodCategory(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        max_length=100,
        unique=True
    )
    description = models.CharField(
        max_length=255
    )


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
    name = models.CharField(
        max_length=100,
        unique=True
    )
    description = models.CharField(
        max_length=255
    )
    serving_size = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    serving_unit = models.CharField(
        max_length=20,
        choices=SERVING_UNIT_CHOICES
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )


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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["food", "nutrient_type"],
                name="unique_nutrient_type_per_food"
            )
        ]


class ConsumptionRecord(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user_id = models.UUIDField()
    consumed_at = models.DateTimeField()
    notes = models.CharField(
        max_length=255,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


class ConsumptionItem(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    consumption = models.ForeignKey(
        ConsumptionRecord,
        on_delete=models.CASCADE,
        related_name="consumption_items"
    )
    food = models.ForeignKey(
        Food,
        on_delete=models.PROTECT,
        related_name="consumption_items"
    )
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    calories = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    protein = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    carbohydrates = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    fat = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    fiber = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    sugar = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    sodium = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
