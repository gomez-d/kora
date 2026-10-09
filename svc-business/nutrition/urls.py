from django.urls import path
from .views import (
    HealthCheckView,
    NutritionalProfileListCreateView,
    FoodCreateView,
    FoodCategoryCreateView
)

urlpatterns = [
    path(
        "health/",
        HealthCheckView.as_view(),
        name="health-check"
    ),
    path(
        "nutritional-profiles/",
        NutritionalProfileListCreateView.as_view(),
        name="nutritional-profile-list-create"
    ),
    path(
        "food-categories/",
        FoodCategoryCreateView.as_view(),
        name="food-category-create"
    ),
    path(
        "foods/",
        FoodCreateView.as_view(),
        name="foods-create"
    )
]
