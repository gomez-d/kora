
import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import transaction
from nutrition.models import Food, FoodCategory, FoodNutrient

alimentos = [
    ("Arroz blanco cocido", "Cereales", 100, "g", 130, 2.7, 28.2, 0.3),
    ("Huevo entero cocido", "Proteínas", 50, "g", 78, 6.3, 0.6, 5.3),
    ("Pechuga de pollo cocida", "Proteínas", 100, "g", 165, 31, 0, 3.6),
    ("Manzana", "Frutas", 100, "g", 52, 0.3, 13.8, 0.2),
    ("Avena seca", "Cereales", 100, "g", 389, 16.9, 66.3, 6.9),
    ("Salmon cocido", "Proteínas", 100, "g", 206, 22.1, 0, 12.4),
    ("Platano", "Frutas", 100, "g", 89, 1.1, 22.8, 0.3),
    ("Frijoles cocidos", "Legumbres", 100, "g", 127, 8.7, 22.8, 0.5),
    ("Leche entera", "Lacteos", 100, "ml", 61, 3.2, 4.8, 3.3),
    ("Tortilla de maiz", "Cereales", 30, "g", 65, 1.7, 13.5, 0.9),
]

with transaction.atomic():
    for name, category_name, size, unit, calories, protein, carbs, fat in alimentos:
        category, _ = FoodCategory.objects.get_or_create(
            name=category_name,
            defaults={"description": "Categoria para pruebas"},
        )

        food, created = Food.objects.get_or_create(
            name=name,
            defaults={
                "category": category,
                "description": f"{name} para pruebas del catalogo",
                "serving_size": Decimal(str(size)),
                "serving_unit": unit,
            },
        )

        if created:
            for nutrient_type, amount, nutrient_unit in [
                ("calories", calories, "kcal"),
                ("protein", protein, "g"),
                ("carbohydrates", carbs, "g"),
                ("fat", fat, "g"),
            ]:
                FoodNutrient.objects.create(
                    food=food,
                    nutrient_type=nutrient_type,
                    amount=Decimal(str(amount)),
                    unit=nutrient_unit,
                )

        print("Creado" if created else "Ya existia", "-", name)

print("Total de alimentos:", Food.objects.count())
print("Total de nutrientes:", FoodNutrient.objects.count())
