from django.db import models

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


class Food(models.Model):
    name = models.CharField(max_length=150)
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
