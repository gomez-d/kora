from rest_framework.schemas.openapi import SchemaGenerator


class UnstructuredDataSchemaGenerator(SchemaGenerator):
    """
    Generate the OpenAPI schema for the unstructured data service.
    """

    def get_schema(self, request=None, public=False):
        """
        Build the OpenAPI schema with explicit MongoDB document contracts.
        """

        schema = {
            'openapi': '3.0.2',
            'info': {
                'title': 'Kora Unstructured Data API',
                'description': (
                    'OpenAPI documentation for the Kora '
                    'unstructured data service.'
                ),
                'version': '1.0.0',
            },
            'paths': {
                '/api/documents/': self._create_document_path(),
                '/api/documents/{document_type}/': (
                    self._document_list_path()
                ),
                '/api/documents/{document_type}/{document_id}/': (
                    self._document_detail_path()
                ),
                '/api/documents/identity-events/': (
                    self._identity_event_path()
                ),
            },
            'components': {
                'schemas': self._schemas(),
            },
        }

        return schema

    def _schemas(self):
        """
        Define reusable schemas for MongoDB documents.
        """

        return {
            'AIRecommendation': {
                'type': 'object',
                'properties': {
                    '_id': {
                        'type': 'string',
                        'readOnly': True,
                    },
                    'user_id': {
                        'type': 'string',
                        'format': 'uuid',
                    },
                    'created_at': {
                        'type': 'string',
                        'format': 'date-time',
                        'readOnly': True,
                    },
                    'model': {
                        'type': 'string',
                    },
                    'input_context': {
                        'type': 'object',
                        'additionalProperties': True,
                    },
                    'recommendation': {
                        'type': 'string',
                    },
                    'metadata': {
                        'type': 'object',
                        'additionalProperties': True,
                    },
                },
                'required': [
                    'user_id',
                    'model',
                    'input_context',
                    'recommendation',
                ],
            },
            'MLResult': {
                'type': 'object',
                'properties': {
                    '_id': {
                        'type': 'string',
                        'readOnly': True,
                    },
                    'user_id': {
                        'type': 'string',
                        'format': 'uuid',
                    },
                    'created_at': {
                        'type': 'string',
                        'format': 'date-time',
                        'readOnly': True,
                    },
                    'model': {
                        'type': 'string',
                    },
                    'input_context': {
                        'type': 'object',
                        'additionalProperties': True,
                    },
                    'result': {
                        'type': 'object',
                        'additionalProperties': True,
                    },
                    'metadata': {
                        'type': 'object',
                        'additionalProperties': True,
                    },
                },
                'required': [
                    'user_id',
                    'model',
                    'input_context',
                    'result',
                ],
            },
            'LogDocument': {
                'type': 'object',
                'properties': {
                    '_id': {
                        'type': 'string',
                        'readOnly': True,
                    },
                    'timestamp': {
                        'type': 'string',
                        'format': 'date-time',
                        'readOnly': True,
                    },
                    'service': {
                        'type': 'string',
                    },
                    'level': {
                        'type': 'string',
                    },
                    'event': {
                        'type': 'string',
                    },
                    'data': {
                        'type': 'object',
                        'additionalProperties': True,
                    },
                    'metadata': {
                        'type': 'object',
                        'additionalProperties': True,
                    },
                },
                'required': [
                    'service',
                    'level',
                    'event',
                    'data',
                ],
            },
            'CreateDocumentRequest': {
                'type': 'object',
                'properties': {
                    'document_type': {
                        'type': 'string',
                        'enum': [
                            'ai_recommendations',
                            'ml_results',
                            'logs',
                        ],
                    },
                    'document': {
                        'type': 'object',
                        'additionalProperties': True,
                    },
                },
                'required': [
                    'document_type',
                    'document',
                ],
            },
            'ValidationError': {
                'type': 'object',
                'additionalProperties': True,
            },
            'NotFoundResponse': {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                    },
                },
            },
            'IdentityEventRequest': {
                'type': 'object',
                'additionalProperties': True,
            },
        }

    def _document_type_parameter(self):
        """
        Define the supported MongoDB document type path parameter.
        """

        return {
            'name': 'document_type',
            'in': 'path',
            'required': True,
            'schema': {
                'type': 'string',
                'enum': [
                    'ai_recommendations',
                    'ml_results',
                    'logs',
                ],
            },
        }

    def _create_document_path(self):
        """
        Document generic MongoDB document creation.
        """

        return {
            'post': {
                'operationId': 'createDocument',
                'summary': 'Create an unstructured document',
                'tags': ['Unstructured Data'],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': (
                                    '#/components/schemas/'
                                    'CreateDocumentRequest'
                                ),
                            },
                        },
                    },
                },
                'responses': {
                    '201': {
                        'description': 'Document created successfully.',
                    },
                    '400': {
                        'description': 'Invalid document data.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ValidationError'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }

    def _document_list_path(self):
        """
        Document list operations by document type.
        """

        return {
            'get': {
                'operationId': 'listDocuments',
                'summary': 'List documents by type',
                'tags': ['Unstructured Data'],
                'parameters': [
                    self._document_type_parameter(),
                ],
                'responses': {
                    '200': {
                        'description': 'Documents retrieved successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'additionalProperties': True,
                                    },
                                },
                            },
                        },
                    },
                    '400': {
                        'description': 'Unsupported document type.',
                    },
                },
            },
        }

    def _document_detail_path(self):
        """
        Document detail, partial update, and deletion operations.
        """

        document_id = {
            'name': 'document_id',
            'in': 'path',
            'required': True,
            'schema': {
                'type': 'string',
            },
        }

        parameters = [
            self._document_type_parameter(),
            document_id,
        ]

        return {
            'get': {
                'operationId': 'retrieveDocument',
                'summary': 'Retrieve a document',
                'tags': ['Unstructured Data'],
                'parameters': parameters,
                'responses': {
                    '200': {
                        'description': 'Document retrieved successfully.',
                    },
                    '404': {
                        'description': 'Document not found.',
                    },
                },
            },
            'patch': {
                'operationId': 'updateDocument',
                'summary': 'Partially update a document',
                'tags': ['Unstructured Data'],
                'parameters': parameters,
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'additionalProperties': True,
                            },
                        },
                    },
                },
                'responses': {
                    '200': {
                        'description': 'Document updated successfully.',
                    },
                    '400': {
                        'description': 'Invalid document data.',
                    },
                    '404': {
                        'description': 'Document not found.',
                    },
                },
            },
            'delete': {
                'operationId': 'deleteDocument',
                'summary': 'Delete a document',
                'tags': ['Unstructured Data'],
                'parameters': parameters,
                'responses': {
                    '204': {
                        'description': 'Document deleted successfully.',
                    },
                    '404': {
                        'description': 'Document not found.',
                    },
                },
            },
        }

    def _identity_event_path(self):
        """
        Document identity event creation.
        """

        return {
            'post': {
                'operationId': 'createIdentityEvent',
                'summary': 'Store an identity service event',
                'tags': ['Unstructured Data'],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': (
                                    '#/components/schemas/'
                                    'IdentityEventRequest'
                                ),
                            },
                        },
                    },
                },
                'responses': {
                    '201': {
                        'description': 'Identity event stored successfully.',
                    },
                    '400': {
                        'description': 'Invalid identity event data.',
                    },
                },
            },
        }