from django.urls import path
from users.views import HealthCheckView, UserRegistrationView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('register/', UserRegistrationView.as_view(), name='user-register')

]