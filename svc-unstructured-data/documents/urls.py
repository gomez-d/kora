from django.urls import path
from documents.views import (
    DocumentCreateView,
    DocumentDetailView,
    DocumentListView
)

urlpatterns = [
    # Endpoint used to create flexible documents in MongoDB.
    path('', DocumentCreateView.as_view(), name='document-create'),

    # Endpoint used to retrieve all documents from a collection.
    path('<str:document_type>/', DocumentListView.as_view(), name='document-list',),

    # Endpoint used to retrieve a specific document by its MongoDB ID.
    path('<str:document_type>/<str:document_id>/', DocumentDetailView.as_view(), name='document-detail',),
]