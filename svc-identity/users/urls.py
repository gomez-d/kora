from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    HealthCheckView,
    UserView,
    UserRegistrationView,
    UserDetailView,
    UserUpdateView,
    UserLoginView
)

urlpatterns = [
    path(
        'health/',
        HealthCheckView.as_view(),
        name='health-check'
    ),
    path(
        'users/',
        UserView.as_view(),
        name='users'
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
        'users/<uuid:user_id>/update/',
        UserUpdateView.as_view(),
        name='user-update'
    ),
    path(
        'login/',
        UserLoginView.as_view(),
        name="user-login"
    ),
    path(
        'token/refresh/',
        TokenRefreshView.as_view(),
        name='token-refresh'
    )
]
