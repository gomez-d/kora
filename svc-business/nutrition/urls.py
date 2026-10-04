from django.urls import path
from .views import NutritionalProfileListCreateView

urlpatterns = [
    path(
        "nutritional-profiles/",
        NutritionalProfileListCreateView.as_view(),
        name="nutritional-profile-list-create"
    )
]
