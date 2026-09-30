from django.urls import path
from users.views import HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check')
]