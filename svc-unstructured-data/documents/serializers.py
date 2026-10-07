from rest_framework import serializers

class FlexibleDocumentSerializer(serializers.Serializer):
    """
    Serializer used to validate flexible documents before storing them
    in MongoDB.

    The document_type field determines the target collection, while 
    document accepts a flexible dictionary structure.
    """

    document_type = serializers.ChoiceField(
        choices=[
            'ai_recommendations',
            'ml_results',
            'logs'
        ]
    )

    # Flexible document content stored in MongoDB.
    # Its internal structure may vary depending on the document type.
    document = serializers.DictField()

    def validate(self, attrs):
        """
        Validate fields required by specific document types.

        AI recommendations and ML results must contain a valid UUID
        identifying the related Kora user.
        """

        document_type = attrs['document_type']
        document = attrs['document']

        if document_type in ['ai_recommendations', 'ml_results']:
            if 'user_id' not in document:
                raise serializers.ValidationError(
                    {
                        'document': {
                            'user_id': ['This field is required.']
                        }
                    }
                )

            # Validate and convert the received value to a UUID object.
            uuid_field = serializers.UUIDField()

            try:
                document['user_id'] = uuid_field.run_validation(
                    document['user_id']
                )
            except serializers.ValidationError:
                raise serializers.ValidationError(
                    {
                        'document': {
                            'user_id': ['Must be a valid UUID.']
                        }
                    }
                )

        return attrs