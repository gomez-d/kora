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

        required_fields = {
            'ai_recommendations': [
                'user_id',
                'model',
                'input_context',
                'recommendation',
            ],
            'ml_results': [
                'user_id',
                'model',
                'input_context',
                'result',
            ],
            'logs': [
                'service',
                'level',
                'event',
                'data',
            ],
        }

        # Validate required fields for the selected document type.
        missing_fields = [
            field
            for field in required_fields[document_type]
            if field not in document
        ]

        if missing_fields:
            errors = {
                field: ['This field is required.']
                for field in missing_fields
            }

            raise serializers.ValidationError(
                {
                    'document': errors
                }
            )

        # Validate user_id as UUID for documents related to Kora users.
        if document_type in ['ai_recommendations', 'ml_results']:
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

        # Validate minimum field types while preserving flexible content.
        self.__validate_field_types(document_type, document)

        return attrs

    def __validate_field_types(self, document_type, document):
        """
        Validate only the minimum expected data types for each document
        type while allowing additional flexible fields.
        """
        errors = {}

        if document_type in ['ai_recommendations', 'ml_results']:
            if not isinstance(document['model'], str):
                errors['model'] = ['Must be a string.']

            if not isinstance(document['input_context'], dict):
                errors['input_context'] = ['Must be an object.']

        if document_type == 'ai_recommendations':
            if not isinstance(document['recommendation'], (str, dict)):
                errors['recommendation'] = [
                    'Must be a string or an object.'
                ]

        if document_type == 'ml_results':
            if not isinstance(document['result'], dict):
                errors['result'] = ['Must be an object.']

        if document_type == 'logs':
            if not isinstance(document['service'], str):
                errors['service'] = ['Must be a string.']

            if not isinstance(document['level'], str):
                errors['level'] = ['Must be a string.']

            if not isinstance(document['event'], str):
                errors['event'] = ['Must be a string.']

            if not isinstance(document['data'], dict):
                errors['data'] = ['Must be an object.']

        if 'metadata' in document and not isinstance(
            document['metadata'],
            dict
        ):
            errors['metadata'] = ['Must be an object.']

        if errors:
            raise serializers.ValidationError(
                {
                    'document': errors
                }
            )

class FlexibleDocumentUpdateSerializer(serializers.Serializer):
    """
    Serializer used to validate partial update for flexible MongoDB documents.
    """

    # Flexible fields that will be updated in the existing document.
    document = serializers.DictField()

    def validate_document(self, value):
        """
        Prevent modification of fields managed internally by MongoDB or by the service.
        """
        if '_id' in value:
            raise serializers.ValidationError(
                'The _id field cannot be modified.'
            )

        return value