from rest_framework.schemas.openapi import SchemaGenerator


class IdentitySchemaGenerator(SchemaGenerator):
    """
    Generate the OpenAPI schema for the identity service.
    """

    def get_schema(self, request=None, public=False):
        """
        Build the OpenAPI schema with explicit identity contracts.
        """

        schema = super().get_schema(
            request=request,
            public=public,
        )

        schema['paths'] = {
            '/api/users/health/': self._health_path(),
            '/api/users/register/': self._register_path(),
        }

        schema['components'] = {
            'schemas': {
                'HealthResponse': {
                    'type': 'object',
                    'properties': {
                        'status': {
                            'type': 'string',
                            'example': 'ok',
                        },
                        'service': {
                            'type': 'string',
                            'example': 'identity',
                        },
                    },
                    'required': [
                        'status',
                        'service',
                    ],
                },
                'UserRegistrationRequest': {
                    'type': 'object',
                    'properties': {
                        'username': {
                            'type': 'string',
                        },
                        'email': {
                            'type': 'string',
                            'format': 'email',
                        },
                        'password': {
                            'type': 'string',
                            'format': 'password',
                            'writeOnly': True,
                        },
                        'first_name': {
                            'type': 'string',
                        },
                        'last_name': {
                            'type': 'string',
                        },
                    },
                    'required': [
                        'username',
                        'email',
                        'password',
                        'first_name',
                        'last_name',
                    ],
                },
                'UserRegistrationData': {
                    'type': 'object',
                    'properties': {
                        'user_id': {
                            'type': 'string',
                            'format': 'uuid',
                        },
                        'username': {
                            'type': 'string',
                        },
                        'email': {
                            'type': 'string',
                            'format': 'email',
                        },
                        'first_name': {
                            'type': 'string',
                        },
                        'last_name': {
                            'type': 'string',
                        },
                    },
                },
                'UserRegistrationResponse': {
                    'type': 'object',
                    'properties': {
                        'success': {
                            'type': 'boolean',
                            'example': True,
                        },
                        'message': {
                            'type': 'string',
                            'example': 'User registered successfully.',
                        },
                        'data': {
                            '$ref': (
                                '#/components/schemas/'
                                'UserRegistrationData'
                            ),
                        },
                    },
                },
                'ValidationErrorResponse': {
                    'type': 'object',
                    'properties': {
                        'success': {
                            'type': 'boolean',
                            'example': False,
                        },
                        'message': {
                            'type': 'string',
                            'example': 'Validation error.',
                        },
                        'errors': {
                            'type': 'object',
                            'additionalProperties': True,
                        },
                    },
                },
            },
        }

        return schema

    def _health_path(self):
        """
        Document the identity service health endpoint.
        """

        return {
            'get': {
                'operationId': 'identityHealthCheck',
                'summary': 'Check identity service health',
                'tags': ['Identity'],
                'responses': {
                    '200': {
                        'description': 'Identity service is available.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'HealthResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }

    def _register_path(self):
        """
        Document user registration.
        """

        return {
            'post': {
                'operationId': 'registerUser',
                'summary': 'Register a new Kora user',
                'tags': ['Identity'],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': (
                                    '#/components/schemas/'
                                    'UserRegistrationRequest'
                                ),
                            },
                        },
                    },
                },
                'responses': {
                    '201': {
                        'description': 'User registered successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'UserRegistrationResponse'
                                    ),
                                },
                            },
                        },
                    },
                    '400': {
                        'description': 'Invalid registration data.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ValidationErrorResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }