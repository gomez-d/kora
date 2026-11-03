from rest_framework.schemas.openapi import SchemaGenerator

class KoraSchemaGenerator(SchemaGenerator):
    """
    Generate the OpenAPI schema exposed by the Kora API Gateway.

    Gateway proxy routes are dynamic, so their public V1 contracts
    are documented explicitly instead of relying only an automatic
    DRF route introspection.
    """

    def get_schema(self, request=None, public=False):
        """
        Build the OpenAPI shcema and replace dynamic proxy paths
        with the explicit public API contracts.
        """

        schema = super().get_schema(
            request=request,
            public=public
        )

        schema['paths'] = {
            '/api/health/': self._gateway_health_path(),
            '/api/identity/users/health/': self._identity_health_path(),
            '/api/identity/users/register/': self._identity_register_path(),
            '/api/business/health/': self._business_health_path(),
            '/api/business/nutritional-profiles/': (
                self._nutritional_profiles_path()
            ),
            '/api/business/food-categories/': (
                self._food_categories_path()
            ),
            '/api/business/foods/': self._foods_path(),
            '/api/business/foods/{food_id}/': self._food_detail_path(),
            '/api/business/consumptions/': self._consumptions_path(),
            '/api/ai/process': self._ai_process_path(),
            '/api/ai/vision/analyze': self._ai_vision_path(),
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
                            'example': 'api_gateway',
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
                'ServiceUnavailableResponse': {
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                        },
                    },
                },
                'NutritionalProfile': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'string',
                            'format': 'uuid',
                        },
                        'user_id': {
                            'type': 'string',
                            'format': 'uuid',
                        },
                        'age': {
                            'type': 'integer',
                        },
                        'sex': {
                            'type': 'string',
                        },
                        'weight': {
                            'type': 'number',
                        },
                        'height': {
                            'type': 'number',
                        },
                        'activity_level': {
                            'type': 'string',
                        },
                        'nutrition_goal': {
                            'type': 'string',
                        },
                    },
                },
                'FoodCategory': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'string',
                            'format': 'uuid',
                        },
                        'name': {
                            'type': 'string',
                        },
                        'description': {
                            'type': 'string',
                        },
                    },
                },
                'BusinessValidationError': {
                    'type': 'object',
                    'additionalProperties': True,
                },
                'FoodNutrient': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'string',
                            'format': 'uuid',
                            'readOnly': True,
                        },
                        'nutrient_type': {
                            'type': 'string',
                        },
                        'amount': {
                            'type': 'number',
                        },
                        'unit': {
                            'type': 'string',
                        },
                    },
                    'required': [
                        'nutrient_type',
                        'amount',
                        'unit',
                    ],
                },
                'FoodRequest': {
                    'type': 'object',
                    'properties': {
                        'category_id': {
                            'type': 'string',
                            'format': 'uuid',
                        },
                        'name': {
                            'type': 'string',
                        },
                            'description': {
                            'type': 'string',
                        },
                        'serving_size': {
                            'type': 'number',
                        },
                        'serving_unit': {
                            'type': 'string',
                        },
                        'nutrients': {
                            'type': 'array',
                            'items': {
                                '$ref': '#/components/schemas/FoodNutrient',
                            },
                        },
                    },
                    'required': [
                        'category_id',
                        'name',
                        'description',
                        'serving_size', 
                        'serving_unit',
                        'nutrients',
                    ],
                },
                'FoodResponse': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'string',
                            'format': 'uuid',
                        },
                        'category': {
                            '$ref': '#/components/schemas/FoodCategory',
                        },
                        'name': {
                            'type': 'string',
                        },
                        'description': {
                            'type': 'string',
                        },
                        'serving_size': {
                            'type': 'number',
                        },
                        'serving_unit': {
                            'type': 'string',
                        },
                        'nutrients': {
                            'type': 'array',
                            'items': {
                                '$ref': '#/components/schemas/FoodNutrient',
                            },
                        },
                        'created_at': {
                            'type': 'string',
                            'format': 'date-time',
                        },
                        'updated_at': {
                            'type': 'string',
                            'format': 'date-time',
                        },
                    },
                },
                'NotFoundResponse': {
                    'type': 'object',
                    'properties': {
                        'detail': {
                            'type': 'string',
                            'example': 'Food not found.',
                        },
                    },
                },
                'ConflictResponse': {
                    'type': 'object',
                    'properties': {
                        'detail': {
                            'type': 'string',
                        },
                    },
                },
                'ConsumptionItem': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'string',
                            'format': 'uuid',
                            'readOnly': True,
                        },
                        'food_id': {
                            'type': 'string',
                            'format': 'uuid',
                        },
                        'quantity': {
                            'type': 'number',
                        },
                        'calories': {
                            'type': 'number',
                        },
                        'protein': {
                            'type': 'number',
                        },
                        'carbohydrates': {
                            'type': 'number',
                        },
                        'fat': {
                            'type': 'number',
                        },
                        'fiber': {
                            'type': 'number',
                        },
                        'sugar': {
                            'type': 'number',
                        },
                        'sodium': {
                            'type': 'number',
                        },
                    },
                },
                'ConsumptionRecord': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'string',
                            'format': 'uuid',
                            'readOnly': True,
                        },
                        'user_id': {
                            'type': 'string',
                            'format': 'uuid',
                        },
                        'consumed_at': {
                            'type': 'string',
                            'format': 'date-time',
                        },
                        'notes': {
                            'type': 'string',
                        },
                        'consumption_items': {
                            'type': 'array',
                            'items': {
                                '$ref': '#/components/schemas/ConsumptionItem',
                            },
                        },
                        'created_at': {
                            'type': 'string',
                            'format': 'date-time',
                            'readOnly': True,
                        },
                    },
                    'required': [
                        'user_id',
                        'consumed_at',
                        'notes',
                        'consumption_items',
                    ],
                },
                'AIRequest': {
                    'type': 'object',
                    'properties': {
                        'type': {
                            'type': 'string',
                            'enum': ['llm'],
                        },
                        'prompt': {
                            'type': 'string',
                            'minLength': 1,
                        },
                        'user_id': {
                            'type': 'string',
                            'nullable': True,
                        },
                    },
                    'required': [
                        'type',
                        'prompt',
                    ],
                },
                'LLMResponse': {
                    'type': 'object',
                    'properties': {
                        'success': {
                            'type': 'boolean',
                        },
                        'type': {
                            'type': 'string',
                            'enum': ['llm'],
                        },
                        'response': {
                            'type': 'string',
                        },
                    },
                    'required': [
                        'success',
                        'type',
                        'response',
                    ],
                },
                'Detection': {
                    'type': 'object',
                    'properties': {
                        'food': {
                            'type': 'string',
                        },
                        'confidence': {
                            'type': 'number',
                            'minimum': 0.0,
                            'maximum': 1.0,
                        },
                    },
                    'required': [
                        'food',
                        'confidence',
                    ],
                },
                'VisionResponse': {
                    'type': 'object',
                    'properties': {
                        'success': {
                            'type': 'boolean',
                        },
                        'detections': {
                            'type': 'array',
                            'items': {
                                '$ref': '#/components/schemas/Detection',
                            },
                        },
                    },
                    'required': [
                        'success',
                        'detections',
                    ],
                },
                'AIErrorResponse': {
                    'type': 'object',
                    'properties': {
                        'detail': {
                            'type': 'string',
                        },
                    },
                }, 
            },
        }

        return schema

    def _gateway_health_path(self):
        """
        Document the API Gateway health check.
        """

        return {
            'get': {
                'operationId': 'gatewayHealthCheck',
                'summary': 'Check API Gateway health',
                'tags': ['Gateway'],
                'responses': {
                    '200': {
                        'description': 'Gateway is available.',
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

    def _identity_health_path(self):
        """
        Document the identity service health check exposed
        through the API Gateway.
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
                    '503': {
                        'description': 'Identity service is unavailable.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ServiceUnavailableResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }

    def _identity_register_path(self):
        """
        Document user registration exposed through the API Gateway.
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
                    '503': {
                        'description': 'Identity service is unavailable.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ServiceUnavailableResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }

    def _business_health_path(self):
        """
        Document the business service health check exposed
        through the API Gateway.
        """

        return  {
            'get': {
                'operationId': 'businessHealthCheck',
                'summary': 'Check business service health',
                'tags': ['Business'],
                'responses': {
                    '200': {
                        'description': 'Business service is available.',
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
                    '503': {
                        'description': 'Business service is unavailable.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ServiceUnavailableResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }

    def _nutritional_profiles_path(self):
        """
        Document nutritional profile list and creation endpoints.
        """

        return {
            'get': {
                'operationId': 'listNutritionalProfiles',
                'summary': 'List nutritional profiles',
                'tags': ['Business'],
                'responses': {
                    '200': {
                        'description': 'Nutritional profiles retrieved successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'array',
                                    'items': {
                                        '$ref': (
                                            '#/components/schemas/'
                                            'NutritionalProfile'
                                        ),
                                    },
                                },
                            },
                        },
                    },
                    '503': {
                        'description': 'Business service is unavailable.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ServiceUnavailableResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
            'post': {
                'operationId': 'createNutritionalProfile',
                'summary': 'Create a nutritional profile',
                'tags': ['Business'],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': (
                                    '#/components/schemas/'
                                    'NutritionalProfile'
                                ),
                            },
                        },
                    },
                },
                'responses': {
                    '201': {
                        'description': 'Nutritional profile created successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'NutritionalProfile'
                                    ),
                                },
                            },
                        },
                    },
                    '400': {
                        'description': 'Invalid nutritional profile data.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'BusinessValidationError'
                                    ),
                                },
                            },
                        },
                    },
                    '503': {
                        'description': 'Business service is unavailable.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ServiceUnavailableResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }

    def _food_categories_path(self):
        """
        Document food category creation.
        """

        return {
            'post': {
                'operationId': 'createFoodCategory',
                'summary': 'Create a food category',
                'tags': ['Business'],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': (
                                    '#/components/schemas/'
                                    'FoodCategory'
                                ),
                            },
                        },
                    },
                },
                'responses': {
                    '201': {
                        'description': 'Food category created successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'FoodCategory'
                                    ),
                                },
                            },
                        },
                    },
                    '400': {
                        'description': 'Invalid food category data.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'BusinessValidationError'
                                    ),
                                },
                            },
                        },
                    },
                    '503': {
                        'description': 'Business service is unavailable.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ServiceUnavailableResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }

    def _foods_path(self):
        """
        Document food listing and creation endpoints.
        """

        return {
            'get': {
                'operationId': 'listFoods',
                'summary': 'List foods',
                'tags': ['Business'],
                'parameters': [
                    {
                        'name': 'search',
                        'in': 'query',
                        'required': False,
                        'schema': {
                            'type': 'string',
                        },
                    },
                    {
                        'name': 'category_id',
                        'in': 'query',
                        'required': False,
                        'schema': {
                            'type': 'string',
                            'format': 'uuid',
                        },
                    },
                    {
                        'name': 'ordering',
                        'in': 'query',
                        'required': False,
                        'schema': {
                            'type': 'string',
                            'enum': [
                                'name',
                                '-name',
                                'created_at',
                                '-created_at',
                            ],
                            'default': 'name',
                        },
                    },
                ],
                'responses': {
                    '200': {
                        'description': 'Foods retrieved successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'additionalProperties': True,
                                },
                            },
                        },
                    },
                    '503': {
                        'description': 'Business service is unavailable.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ServiceUnavailableResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
            'post': {
                'operationId': 'createFood',
                'summary': 'Create a food',
                'tags': ['Business'],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/FoodRequest',
                            },
                        },
                    },
                },
                'responses': {
                    '201': {
                        'description': 'Food created successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/FoodResponse',
                                },
                            },
                        },
                    },
                    '400': {
                        'description': 'Invalid food data.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'BusinessValidationError'
                                    ),
                                },
                            },
                        },
                    },
                    '503': {
                        'description': 'Business service is unavailable.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ServiceUnavailableResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }

    def _food_detail_path(self):
        """
        Document food retrieval, update, partial update, and deletion.
        """

        parameter = {
            'name': 'food_id',
            'in': 'path',
            'required': True,
            'schema': {
                'type': 'string',
                'format': 'uuid',
            },
        }

        success_response = {
            'description': 'Food operation completed successfully.',
            'content': {
                'application/json': {
                    'schema': {
                        '$ref': '#/components/schemas/FoodResponse',
                    },
                },
            },
        }

        not_found_response = {
            'description': 'Food not found.',
            'content': {
                'application/json': {
                    'schema': {
                        '$ref': '#/components/schemas/NotFoundResponse',
                    },
                },
            },
        }

        return {
            'get': {
                'operationId': 'retrieveFood',
                'summary': 'Retrieve a food',
                'tags': ['Business'],
                'parameters': [parameter],
                'responses': {
                    '200': success_response,
                    '404': not_found_response,
                    '503': {
                        'description': 'Business service is unavailable.',
                    },
                },
            },
            'put': {
                'operationId': 'updateFood',
                'summary': 'Update a food',
                'tags': ['Business'],
                'parameters': [parameter],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/FoodRequest',
                            },
                        },
                    },
                },
                'responses': {
                    '200': success_response,
                    '400': {
                        'description': 'Invalid food data.',
                    },
                    '404': not_found_response,
                    '503': {
                        'description': 'Business service is unavailable.',
                    },
                },
            },
            'patch': {
                'operationId': 'partiallyUpdateFood',
                'summary': 'Partially update a food',
                'tags': ['Business'],
                'parameters': [parameter],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/FoodRequest',
                            },
                        },
                    },
                },
                'responses': {
                    '200': success_response,
                    '400': {
                        'description': 'Invalid food data.',
                    },
                    '404': not_found_response,
                    '503': {
                        'description': 'Business service is unavailable.',
                    },
                },
            },
            'delete': {
                'operationId': 'deleteFood',
                'summary': 'Delete a food',
                'tags': ['Business'],
                'parameters': [parameter],
                'responses': {
                    '204': {
                        'description': 'Food deleted successfully.',
                    },
                    '404': not_found_response,
                    '409': {
                        'description': (
                            'Food is referenced by consumption records.'
                        ),
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ConflictResponse'
                                    ),
                                },
                            },
                        },
                    },
                    '503': {
                        'description': 'Business service is unavailable.',
                    },
                },
            },
        }

    def _consumptions_path(self):
        """
        Document consumption record creation.
        """

        return {
            'post': {
                'operationId': 'createConsumption',
                'summary': 'Create a consumption record',
                'tags': ['Business'],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': (
                                    '#/components/schemas/'
                                    'ConsumptionRecord'
                                ),
                            },
                        },
                    },
                },
                'responses': {
                    '201': {
                        'description': 'Consumption record created successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ConsumptionRecord'
                                    ),
                                },
                            },
                        },
                    },
                    '400': {
                        'description': 'Invalid consumption data.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'BusinessValidationError'
                                    ),
                                },
                            },
                        },
                    },
                    '503': {
                        'description': 'Business service is unavailable.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ServiceUnavailableResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }

    def _ai_process_path(self):
        """
        Document LLM processing exposed through the API Gateway.
        """

        return {
            'post': {
                'operationId': 'processAI',
                'summary': 'Process an LLM request',
                'tags': ['AI'],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/AIRequest',
                            },
                        },
                    },
                },
                'responses': {
                    '200': {
                        'description': 'AI request processed successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/LLMResponse',
                                },
                            },
                        },
                    },
                    '400': {
                        'description': (
                            'Invalid AI request or missing prompt.'
                        ),
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'AIErrorResponse'
                                    ),
                                },
                            },
                        },
                    },
                    '503': {
                        'description': 'AI service is unavailable.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ServiceUnavailableResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }

    def _ai_vision_path(self):
        """
        Document image analysis exposed through the API Gateway.
        """

        return {
            'post': {
                'operationId': 'analyzeVision',
                'summary': 'Analyze an uploaded food image',
                'tags': ['AI'],
                'requestBody': {
                    'required': True,
                    'content': {
                        'multipart/form-data': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'image': {
                                        'type': 'string',
                                        'format': 'binary',
                                    },
                                },
                                'required': [
                                    'image',
                                ],
                            },
                        },
                    },
                },
                'responses': {
                    '200': {
                        'description': 'Image analyzed successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'VisionResponse'
                                    ),
                                },
                            },
                        },
                    },
                    '400': {
                        'description': (
                            'Invalid, empty, or unsupported image.'
                        ),
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'AIErrorResponse'
                                    ),
                                },
                            },
                        },
                    },
                    '503': {
                        'description': 'AI service is unavailable.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'ServiceUnavailableResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }