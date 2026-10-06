from django.urls import include, path
from gateway.views import HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('identity/', include('gateway.identity_urls')),
    path('business/', include('gateway.business_urls'))
]
