from rest_framework.schemas.openapi import SchemaGenerator


class BusinessSchemaGenerator(SchemaGenerator):
    """
    Generate the OpenAPI schema for the business service.
    """

    def get_schema(self, request=None, public=False):
        """
        Build the OpenAPI schema with explicit business contracts,
        authentication, and RBAC authorization requirements.
        """

        schema = {
            'openapi': '3.0.2',
            'info': {
                'title': 'Kora Business API',
                'description': (
                    'OpenAPI documentation for the Kora business service.'
                ),
                'version': '1.0.0',
            },
            'paths': {
                '/api/health/': self._health_path(),
                '/api/nutritional-profiles/': (
                    self._nutritional_profiles_path()
                ),
                '/api/nutritional-profiles/{profile_id}/': (
                    self._nutritional_profile_detail_path()
                ),
                '/api/food-categories/': (
                    self._food_categories_path()
                ),
                '/api/foods/': self._foods_path(),
                '/api/foods/{food_id}/': (
                    self._food_detail_path()
                ),
                '/api/consumptions/': (
                    self._consumptions_path()
                ),
                '/api/consumptions/{consumption_id}/': (
                    self._consumption_detail_path()
                ),
            },
            'components': {
                'securitySchemes': {
                    'bearerAuth': {
                        'type': 'http',
                        'scheme': 'bearer',
                        'bearerFormat': 'JWT',
                    },
                },
                'schemas': self._schemas(),
            },
        }

        return schema

    def _schemas(self):
        """
        Define reusable OpenAPI schemas for the business service.
        """

        return {
            'HealthResponse': {
                'type': 'object',
                'properties': {
                    'status': {
                        'type': 'string',
                        'example': 'ok',
                    },
                    'service': {
                        'type': 'string',
                        'example': 'business',
                    },
                },
                'required': [
                    'status',
                    'service',
                ],
            },
            'NutritionalProfile': {
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
                    'date_of_birth': {
                        'type': 'string',
                        'format': 'date',
                    },
                    'sex': {
                        'type': 'string',
                        'enum': [
                            'MALE',
                            'FEMALE'
                        ],
                    },
                    'weight': {
                        'type': 'number',
                        'exclusiveMinimum': 0,
                    },
                    'height': {
                        'type': 'number',
                        'exclusiveMinimum': 0,
                    },
                    'activity_level': {
                        'type': 'string',
                        'enum': [
                            'NONE',
                            'LOW', 
                            'MODERATE',
                            'HIGH',
                            'VERY_HIGH'
                        ],
                    },
                    'created_at': {
                        'type': 'string',
                        'format': 'date-time',
                        'readOnly': True
                    },
                    'updated_at': {
                        'type': 'string',
                        'format': 'date-time',
                        'readOnly': True,
                    },
                },
                'required': [
                    'user_id',
                    'date_of_birth',
                    'sex',
                    'weight',
                    'height',
                    'activity_level'
                ],
            },
            'FoodCategory': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'string',
                        'format': 'uuid',
                        'readOnly': True,
                    },
                    'name': {
                        'type': 'string',
                    },
                    'description': {
                        'type': 'string',
                    },
                },
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
                        'enum': [
                            'CALORIES',
                            'PROTEIN',
                            'CARBOHYDRATES',
                            'FAT',
                            'FIBER',
                            'SUGAR',
                            'SODIUM'
                        ],
                    },
                    'amount': {
                        'type': 'number',
                        'minimum': 0,
                    },
                    'unit': {
                        'type': 'string',
                        'enum': [
                            'G',
                            'MG',
                            'KCAL'
                        ],
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
                        'enum': [100],
                    },
                    'serving_unit': {
                        'type': 'string',
                        'enum': [
                            'G',
                            'ML',
                            'UNIT',
                        ],
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
                        'enum': [
                            'G',
                            'ML',
                            'UNIT',
                        ],
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
            'FoodWriteResponse': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'string',
                        'format': 'uuid',
                    },
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
                        'enum': [
                            'G',
                            'ML',
                            'UNIT',
                        ],
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
                        'format': 'date-time'
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
                        'exclusiveMinimum': 0,
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
            'ConsumptionItemRequest': {
                'type': 'object',
                'properties': {
                    'food_id': {
                        'type': 'string',
                        'format': 'uuid',
                    },
                    'quantity': {
                        'type': 'number',
                        'exclusiveMinimum': 0,
                    },
                },
                'required': [
                    'food_id',
                    'quantity',
                ],
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
            },
            'ConsumptionRecordRequest': {
                'type': 'object',
                'properties': {
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
                            '$ref': (
                                '#/components/schemas/'
                                'ConsumptionItemRequest'
                            ),
                        },
                    },
                },
                'required': [
                    'user_id',
                    'consumed_at',
                    'consumption_items',
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
            'ConflictResponse': {
                'type': 'object',
                'properties': {
                    'detail': {
                        'type': 'string',
                    },
                },
            },
            'UnauthorizedResponse': {
                'type': 'object',
                'properties': {
                    'success': {
                        'type': 'boolean',
                        'example': False,
                    },
                    'code': {
                        'type': 'string',
                        'example': 'unauthorized',
                    },
                    'message': {
                        'type': 'string',
                        'example': (
                            'Authentication credentials are '
                            'missing or invalid.'
                        ),
                    },
                },
                'required': [
                    'success',
                    'code',
                    'message',
                ],
            },
            'ForbiddenResponse': {
                'type': 'object',
                'properties': {
                    'success': {
                        'type': 'boolean',
                        'example': False,
                    },
                    'code': {
                        'type': 'string',
                        'example': 'forbidden',
                    },
                    'message': {
                        'type': 'string',
                        'example': (
                            'You do not have permission to '
                            'perform this operation.'
                        ),
                    },
                },
                'required': [
                    'success',
                    'code',
                    'message',
                ],
            },
        }

    # =========================================================
    # COMMON HELPERS
    # =========================================================

    def _response(self, description, schema_name):
        """
        Build a reusable JSON response definition.
        """

        return {
            'description': description,
            'content': {
                'application/json': {
                    'schema': {
                        '$ref': (
                            f'#/components/schemas/{schema_name}'
                        ),
                    },
                },
            },
        }

    def _unauthorized_response(self):
        """
        Document an authentication failure.
        """

        return self._response(
            'Authentication credentials are missing or invalid.',
            'UnauthorizedResponse',
        )

    def _forbidden_response(self):
        """
        Document an authorization failure.
        """

        return self._response(
            (
                'The authenticated user does not have '
                'the required permission.'
            ),
            'ForbiddenResponse',
        )

    def _bearer_security(self):
        """
        Require a valid JWT Bearer access token.
        """

        return [
            {
                'bearerAuth': [],
            },
        ]

    def _uuid_parameter(self, name, description):
        """
        Build a reusable UUID path parameter.
        """

        return {
            'name': name,
            'in': 'path',
            'required': True,
            'description': description,
            'schema': {
                'type': 'string',
                'format': 'uuid',
            },
        }

    def _health_path(self):
        return {
            'get': {
                'operationId': 'businessHealthCheck',
                'summary': 'Check business service health',
                'description': (
                    'Public endpoint. Authentication is not required.'
                ),
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
                },
            },
        }

    def _nutritional_profiles_path(self):
        return {
            'get': {
                'operationId': 'listNutritionalProfiles',
                'summary': 'List nutritional profiles',
                'description': (
                    'Self-scoped operation. Requires a valid Bearer JWT '
                    'and the `nutritional_profiles.read_self` permission. '
                    'The requested user must match the authenticated user.'
                ),
                'tags': ['Business'],
                'security': self._bearer_security(),
                'responses': {
                    '200': {
                        'description': 'Profiles retrieved successfully.',
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
                    '401': self._unauthorized_response(),
                    '403': self._forbidden_response(),
                },
            },
            'post': {
                'operationId': 'createNutritionalProfile',
                'summary': 'Create a nutritional profile',
                'description': (
                    'Self-scoped operation. Requires a valid Bearer JWT '
                    'and the `nutritional_profiles.create_self` permission. '
                    'The profile must belong to the authenticated user.'
                ),
                'tags': ['Business'],
                'security': self._bearer_security(),
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
                        'description': 'Profile created successfully.',
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
                        'description': 'Invalid profile data.',
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
                    '401': self._unauthorized_response(),
                    '403': self._forbidden_response(),
                },
            },
        }

    def _nutritional_profile_detail_path(self):
        return {
            'patch': {
                'operationId': 'partialUpdateNutritionalProfile',
                'summary': 'Partially update a nutritional profile',
                'description': (
                    'Self-scoped operation. Requires a valid Bearer JWT '
                    'and the `nutritional_profiles.update_self` permission. '
                    'Ownership is verified using the persisted resource '
                    'user_id and the authenticated JWT user_id.'
                ),
                'tags': ['Business'],
                'security': self._bearer_security(),
                'parameters': [
                    self._uuid_parameter(
                        'profile_id',
                        'UUID of the nutritional profile.',
                    ),
                ],
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
                    '200': {
                        'description': (
                            'Nutritional profile updated successfully.'
                        ),
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
                        'description': 'Invalid profile data.',
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
                    '401': self._unauthorized_response(),
                    '403': self._forbidden_response(),
                    '404': {
                        'description': 'Nutritional profile not found.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'NotFoundResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }

    def _food_categories_path(self):
        return {
            'get': {
                'operationId': 'listFoodCategories',
                'summary': 'List food categories',
                'description': (
                    'Authenticated operation. Requires a valid Bearer JWT '
                    'and the `food_categories.read` permission.'
                ),
                'tags': ['Business'],
                'security': self._bearer_security(),
                'responses': {
                    '200': {
                        'description': 'Food categories retrieved successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'array',
                                    'items': {
                                        '$ref': (
                                            '#/components/schemas/'
                                            'FoodCategory'
                                        ),
                                    },
                                },
                            },
                        },
                    },
                    '401': self._unauthorized_response(),
                    '403': self._forbidden_response(),
                },
            },
            'post': {
                'operationId': 'createFoodCategory',
                'summary': 'Create a food category',
                'description': (
                    'Administrative operation. Requires a valid Bearer JWT '
                    'and the `food_categories.create` permission.'
                ),
                'tags': ['Business'],
                'security': self._bearer_security(),
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/FoodCategory',
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
                        'description': 'Invalid category data.',
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
                    '401': self._unauthorized_response(),
                    '403': self._forbidden_response(),
                },
            },
        }

    def _foods_path(self):
        return {
            'get': {
                'operationId': 'listFoods',
                'summary': 'List foods',
                'description': (
                    'Authenticated operation. Requires a valid Bearer JWT '
                    'and the `foods.read` permission.'
                ),
                'tags': ['Business'],
                'security': self._bearer_security(),
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
                    '401': self._unauthorized_response(),
                    '403': self._forbidden_response(),
                },
            },
            'post': {
                'operationId': 'createFood',
                'summary': 'Create a food',
                'description': (
                    'Administrative operation. Requires a valid Bearer JWT '
                    'and the `foods.create` permission.'
                ),
                'tags': ['Business'],
                'security': self._bearer_security(),
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
                                    '$ref': (
                                        '#/components/schemas/'
                                        'FoodWriteResponse'
                                    ),
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
                                        'ValidationError'
                                    ),
                                },
                            },
                        },
                    },
                    '401': self._unauthorized_response(),
                    '403': self._forbidden_response(),
                },
            },
        }

    def _food_detail_path(self):
        food_id = {
            'name': 'food_id',
            'in': 'path',
            'required': True,
            'description': 'UUID of the food.',
            'schema': {
                'type': 'string',
                'format': 'uuid',
            },
        }

        return {
            'get': {
                'operationId': 'retrieveFood',
                'summary': 'Retrieve a food',
                'description': (
                    'Authenticated operation. Requires a valid Bearer JWT '
                    'and the `foods.read` permission.'
                ),
                'tags': ['Business'],
                'security': self._bearer_security(),
                'parameters': [food_id],
                'responses': {
                    '200': {
                        'description': 'Food retrieved successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'FoodResponse'
                                    ),
                                },
                            },
                        },
                    },
                    '401': self._unauthorized_response(),
                    '403': self._forbidden_response(),
                    '404': {
                        'description': 'Food not found.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'NotFoundResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
            'put': {
                'operationId': 'updateFood',
                'summary': 'Update a food',
                'description': (
                    'Administrative operation. Requires a valid Bearer JWT '
                    'and the `foods.update` permission.'
                ),
                'tags': ['Business'],
                'security': self._bearer_security(),
                'parameters': [food_id],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': (
                                    '#/components/schemas/'
                                    'FoodRequest'
                                ),
                            },
                        },
                    },
                },
                'responses': {
                    '200': {
                        'description': 'Food updated successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'FoodResponse'
                                    ),
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
                                        'ValidationError'
                                    ),
                                },
                            },
                        },
                    },
                    '401': self._unauthorized_response(),
                    '403': self._forbidden_response(),
                    '404': {
                        'description': 'Food not found.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'NotFoundResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
            'patch': {
                'operationId': 'partiallyUpdateFood',
                'summary': 'Partially update a food',
                'description': (
                    'Administrative operation. Requires a valid Bearer JWT '
                    'and the `foods.update` permission.'
                ),
                'tags': ['Business'],
                'security': self._bearer_security(),
                'parameters': [food_id],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': (
                                    '#/components/schemas/'
                                    'FoodRequest'
                                ),
                            },
                        },
                    },
                },
                'responses': {
                    '200': {
                        'description': 'Food updated successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'FoodResponse'
                                    ),
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
                                        'ValidationError'
                                    ),
                                },
                            },
                        },
                    },
                    '401': self._unauthorized_response(),
                    '403': self._forbidden_response(),
                    '404': {
                        'description': 'Food not found.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'NotFoundResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
            'delete': {
                'operationId': 'deleteFood',
                'summary': 'Delete a food',
                'description': (
                    'Administrative operation. Requires a valid Bearer JWT '
                    'and the `foods.delete` permission.'
                ),
                'tags': ['Business'],
                'security': self._bearer_security(),
                'parameters': [food_id],
                'responses': {
                    '204': {
                        'description': 'Food deleted successfully.',
                    },
                    '401': self._unauthorized_response(),
                    '403': self._forbidden_response(),
                    '404': {
                        'description': 'Food not found.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'NotFoundResponse'
                                    ),
                                },
                            },
                        },
                    },
                    '409': {
                        'description': (
                            'Food cannot be deleted because it is referenced '
                            'by consumption records.'
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
                },
            },
        }

    def _consumption_detail_path(self):
        return {
            'patch': {
                'operationId': 'partialUpdateConsumption',
                'summary': 'Partially update a consumption record',
                'description': (
                    'Self-scoped operation. Requires a valid Bearer JWT '
                    'and the `consumptions.update_self` permission. '
                    'Ownership is verified using the persisted resource '
                    'user_id and the authenticated JWT user_id.'
                ),
                'tags': ['Business'],
                'security': self._bearer_security(),
                'parameters': [
                    self._uuid_parameter(
                        'consumption_id',
                        'UUID of the consumption record.',
                    ),
                ],
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': (
                                    '#/components/schemas/'
                                    'ConsumptionRecordRequest'
                                ),
                            },
                        },
                    },
                },
                'responses': {
                    '200': {
                        'description': (
                            'Consumption record updated successfully.'
                        ),
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
                                        'ValidationError'
                                    ),
                                },
                            },
                        },
                    },
                    '401': self._unauthorized_response(),
                    '403': self._forbidden_response(),
                    '404': {
                        'description': 'Consumption record not found.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components/schemas/'
                                        'NotFoundResponse'
                                    ),
                                },
                            },
                        },
                    },
                },
            },
        }