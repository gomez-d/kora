from django.urls import path
from gateway.views import HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check')
]