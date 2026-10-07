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

# Map each supported document type to its MongoDB collection.
COLLECTIONS = {
    'ai_recommendations': ai_recommendations_collection,
    'ml_results': ml_results_collection,
    'logs': logs_collection
}

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