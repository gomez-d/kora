from django.urls import path
from documents.views import DocumentCreateView

urlpatterns = [
    # Endpoint used to create flexible documents in MongoDB.
    path('', DocumentCreateView.as_view(), name='document-create')
]