from django.urls import path
from .views import (
    HealthCheckView,
    NutritionalProfileListCreateView,
    FoodView,
    FoodCategoryView,
    FoodDetailView,
    ConsumptionRecordView
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
        FoodCategoryView.as_view(),
        name="food-category"
    ),
    path(
        "foods/",
        FoodView.as_view(),
        name="foods"
    ),
    path(
        "foods/<uuid:food_id>/",
        FoodDetailView.as_view(),
        name="food-detail"
    ),
    path(
        "consumptions/",
        ConsumptionRecordView.as_view(),
        name="consumption-create"
    )
]
