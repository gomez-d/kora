from django.urls import path
from gateway.views import BusinessProxyView

urlpatterns = [
    path(
        '<path:path>/',
        BusinessProxyView.as_view(),
        name='business-health'
    )
]
