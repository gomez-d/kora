from django.urls import path
from .views import HealthCheckView, NutritionalProfileListCreateView, FoodCreateView

urlpatterns = [
    path(
        'health/',
        HealthCheckView.as_view(),
        name='health-check'
    ),
    path(
        'nutritional-profiles/',
        NutritionalProfileListCreateView.as_view(),
        name='nutritional-profile-list-create'
    ),
    path(
        'foods/',
        FoodCreateView.as_view(),
        name='foods-create-view'
    )
]
