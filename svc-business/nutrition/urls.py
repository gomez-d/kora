from django.urls import path
from .views import NutritionalProfileListCreateView, FoodCreateView

urlpatterns = [
    path(
        "nutritional-profiles/",
        NutritionalProfileListCreateView.as_view(),
        name="nutritional-profile-list-create"
    ),
    path(
        "foods/",
        FoodCreateView.as_view(),
        name="foods-create-view"
    )
]
