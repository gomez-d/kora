from datetime import datetime, timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from documents.database import (
    ai_recommendations_collection,
    logs_collection,
    ml_results_collection
)
from documents.serializers import FlexibleDocumentSerializer
from bson import ObjectId
from bson.errors import InvalidId

# Map each supported document type to its MongoDB collection.
COLLECTIONS = {
    'ai_recommendations': ai_recommendations_collection,
    'ml_results': ml_results_collection,
    'logs': logs_collection
}

def serialize_document(document):
    """
    Convert MongoDB-specific values into JSON-compatible values.

    MongoDB objectId values are converted to strings before returning
    the document through the API.
    """
    document['_id'] = str(document['_id'])

    return document

class DocumentCreateView(APIView):
    """
    API endpoint used to create flexible documents in MongoDB.

    The document_type field determines the target collection and the
    document field contains the flexible data to be stored.
    """

    def post(self, request):

        # Validate the basic request structure.
        serializer = FlexibleDocumentSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'message': 'Validation error.',
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        document_type = serializer.validated_data['document_type']
        document = serializer.validated_data['document']

        # Add the default date field depending on the document type.
        if document_type in ['ai_recommendations', 'ml_results']:
            document.setdefault(
                'created_at',
                datetime.now(timezone.utc)
            )

        if document_type == 'logs':
            document.setdefault(
                'timestamp',
                datetime.now(timezone.utc)
            )

        # Select the MongoDB collection associated with the document type.
        collection = COLLECTIONS[document_type]

        # Store the flexible document in MongoDB.
        result = collection.insert_one(document)

        return Response(
            {
                'success': True,
                'message': 'Document created successfully.',
                'data': {
                    'id': str(result.inserted_id),
                    'document_type': document_type
                },
            },
            status=status.HTTP_201_CREATED,
        )

class DocumentListView(APIView):
    """
    API endpoint used to retrieve documents from a MongoDB collection.
    """

    def get(self, request, document_type):
        # Validate that the requested document type is supported.
        if document_type not in COLLECTIONS:
            return Response(
                {
                    'success': False,
                    'message': 'Invalid document type.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        collection = COLLECTIONS[document_type]

        # Retrieve all documents from the selected MongoDB collection.
        documents = [
            serialize_document(document)
            for document in collection.find()
        ]

        return Response(
            {
                'success': True,
                'message': 'Documents retrieved successfully.',
                'data': documents,
            },
            status=status.HTTP_200_OK
        )

class DocumentDetailView(APIView):
    """
    API endpoint used to retrieve a specific MongoDB document by its ID.
    """
    def get(self, request, document_type, document_id):
        # Validate that the requested document type is supported.
        if document_type not in COLLECTIONS:
            return Response(
                {
                    'success': False,
                    'message': 'Invalid document type.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            object_id = ObjectId(document_id)
        except InvalidId:
            return Response(
                {
                    'success': False,
                    'message': 'Invalid document ID.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        collection = COLLECTIONS[document_type]

        # Search for the document using its MongoDB ObjectId.
        document = collection.find_one({'_id': object_id})

        if document is None:
            return Response(
                {
                    'success': False,
                    'message': 'Document not found.',
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                'success': True,
                'message': 'Document retrieved successfully.',
                'data': serialize_document(document)
            },
            status=status.HTTP_200_OK
        )