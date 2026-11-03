from django.urls import path
from users.views import (
    HealthCheckView,
    UserRegistrationView,
    UserDetailView,
    UserLoginView
)

urlpatterns = [
    path(
        'health/',
        HealthCheckView.as_view(),
        name='health-check'
    ),
    path(
        'register/',
        UserRegistrationView.as_view(),
        name='user-register'
    ),
    path(
        'users/<uuid:user_id>/',
        UserDetailView.as_view(),
        name="user-detail"
    ),
    path(
        'login/',
        UserLoginView.as_view(),
        name="user-login"
    )
]
