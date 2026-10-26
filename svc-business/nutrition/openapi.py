from rest_framework.schemas.openapi import SchemaGenerator


class BusinessSchemaGenerator(SchemaGenerator):
    """
    Generate the OpenAPI schema for the business service.
    """

    def get_schema(self, request=None, public=False):
        """
        Build the OpenAPI schema with explicit business contracts.
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
                '/api/food-categories/': self._food_categories_path(),
                '/api/foods/': self._foods_path(),
                '/api/foods/{food_id}/': self._food_detail_path(),
                '/api/consumptions/': self._consumptions_path(),
            },
            'components': {
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
                    'age': {
                        'type': 'integer',
                        'minimum': 1,
                        'maximum': 120,
                    },
                    'sex': {
                        'type': 'string',
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
                    },
                    'amount': {
                        'type': 'number',
                        'minimum': 0,
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
                        'exclusiveMinimum': 0,
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
        }

    def _health_path(self):
        return {
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
                                    '$ref': '#/components/schemas/HealthResponse',
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
                'tags': ['Business'],
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
                },
            },
        }

    def _food_categories_path(self):
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
                    },
                },
            },
        }

    def _foods_path(self):
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
                    },
                },
            },
        }

    def _food_detail_path(self):
        food_id = {
            'name': 'food_id',
            'in': 'path',
            'required': True,
            'schema': {
                'type': 'string',
                'format': 'uuid',
            },
        }

        return {
            'get': {
                'operationId': 'retrieveFood',
                'summary': 'Retrieve a food',
                'tags': ['Business'],
                'parameters': [food_id],
                'responses': {
                    '200': {
                        'description': 'Food retrieved successfully.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/FoodResponse',
                                },
                            },
                        },
                    },
                    '404': {
                        'description': 'Food not found.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/NotFoundResponse',
                                },
                            },
                        },
                    },
                },
            },
            'put': {
                'operationId': 'updateFood',
                'summary': 'Update a food',
                'tags': ['Business'],
                'parameters': [food_id],
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
                    '200': {
                        'description': 'Food updated successfully.',
                    },
                    '400': {
                        'description': 'Invalid food data.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/ValidationError',
                                },
                            },
                        },
                    },
                    '404': {
                        'description': 'Food not found.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/NotFoundResponse',
                                },
                            },
                        },
                    },
                },
            },
            'patch': {
                'operationId': 'partiallyUpdateFood',
                'summary': 'Partially update a food',
                'tags': ['Business'],
                'parameters': [food_id],
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
                    '200': {
                        'description': 'Food updated successfully.',
                    },
                    '400': {
                        'description': 'Invalid food data.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/ValidationError',
                                },
                            },
                        },
                    },
                    '404': {
                        'description': 'Food not found.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/NotFoundResponse',
                                },
                            },
                        },
                    },
                },
            },
            'delete': {
                'operationId': 'deleteFood',
                'summary': 'Delete a food',
                'tags': ['Business'],
                'parameters': [food_id],
                'responses': {
                    '204': {
                        'description': 'Food deleted successfully.',
                    },
                    '404': {
                        'description': 'Food not found.',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/NotFoundResponse',
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
                                    '$ref': '#/components/schemas/ConflictResponse',
                                },
                            },
                        },
                    },
                },
            },
        }

    def _consumptions_path(self):
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
                        'description': 'Consumption created successfully.',
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
                    },
                },
            },
        }