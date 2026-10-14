from django.urls import path
from gateway.views import AIProxyView

urlpatterns = [
    path("<path:path>", AIProxyView.as_view(), name="ai-proxy"),
]