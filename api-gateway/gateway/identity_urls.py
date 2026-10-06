from django.urls import path
from gateway.views import IdentityProxyView

urlpatterns = [
    path(
        '<path:path>/',
        IdentityProxyView.as_view(),
        name='identity-proxy'
    )
]
