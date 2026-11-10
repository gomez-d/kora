from rest_framework.schemas.openapi import SchemaGenerator


class IdentitySchemaGenerator(SchemaGenerator):
    """
    Generate the OpenAPI schema for the identity service.
    """

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request=request, public=public)
        schema["paths"] = {
            # USERS
            "/api/users/health/": self._health_path(),
            "/api/users/register/": self._register_path(),
            "/api/users/login/": self._login_path(),
            "/api/users/token/refresh/": self._refresh_path(),
            "/api/users/users/": self._users_path(),
            "/api/users/users/{user_id}/": self._user_detail_path(),
            "/api/users/users/{user_id}/update/": self._user_update_path(),
            # RBAC
            "/api/rbac/roles/": self._roles_path(),
            "/api/rbac/roles/{role_id}/": self._role_detail_path(),
            "/api/rbac/permissions/": self._permissions_path(),
            "/api/rbac/permissions/{permission_id}/": self._permission_detail_path(),
            "/api/rbac/user-roles/": self._user_roles_path(),
            "/api/rbac/user-roles/{user_role_id}/": self._user_role_detail_path(),
            "/api/rbac/role-permissions/": self._role_permissions_path(),
            "/api/rbac/role-permissions/{role_permission_id}/": self._role_permission_detail_path(),
        }
        schema["components"] = {"schemas": self._schemas()}
        return schema
    # =========================================================
    # SCHEMAS
    # =========================================================

    def _schemas(self):
        return {
            # -------------------------------------------------
            # USERS
            # -------------------------------------------------
            "UserData": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "format": "uuid"},
                    "email": {"type": "string", "format": "email"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "date_of_birth": {
                        "type": "string",
                        "format": "date",
                        "nullable": True,
                    },
                },
            },
            "UserRegistrationRequest": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {
                        "type": "string",
                        "format": "password",
                        "writeOnly": True,
                    },
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "date_of_birth": {"type": "string", "format": "date"},
                },
                "required": [
                    "email",
                    "password",
                    "first_name",
                    "last_name",
                    "date_of_birth",
                ],
            },
            "UserRegistrationResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {
                        "type": "string",
                        "example": "User registered successfully.",
                    },
                    "data": {"$ref": "#/components/schemas/UserData"},
                },
            },
            "UserLoginRequest": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {
                        "type": "string",
                        "format": "password",
                        "writeOnly": True,
                    },
                },
                "required": ["email", "password"],
            },
            "UserLoginResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {
                        "type": "string",
                        "example": "Credentials verified successfully.",
                    },
                    "data": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "format": "uuid"},
                            "access": {"type": "string"},
                            "refresh": {"type": "string"},
                        },
                    },
                },
            },
            "UserListResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/UserData"},
                    },
                },
            },
            "UserDetailResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {"$ref": "#/components/schemas/UserData"},
                },
            },
            "UserUpdateRequest": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "date_of_birth": {
                        "type": "string",
                        "format": "date",
                        "nullable": True,
                    },
                },
                "required": ["email"],
            },
            "UserPartialUpdateRequest": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "date_of_birth": {
                        "type": "string",
                        "format": "date",
                        "nullable": True,
                    },
                },
            },
            "UserUpdateResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {
                        "type": "string",
                        "example": "User updated successfully.",
                    },
                    "data": {"$ref": "#/components/schemas/UserData"},
                },
            },
            "TokenRefreshRequest": {
                "type": "object",
                "properties": {"refresh": {"type": "string"}},
                "required": ["refresh"],
            },
            "TokenRefreshResponse": {
                "type": "object",
                "properties": {"access": {"type": "string"}},
            },
            # -------------------------------------------------
            # RBAC - ROLES
            # -------------------------------------------------
            "RoleRead": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "permissions": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
            "RoleWriteRequest": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["name"],
            },
            "RolePartialUpdateRequest": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                },
            },
            "RoleListResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/RoleRead"},
                    },
                },
            },
            "RoleDetailResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {"$ref": "#/components/schemas/RoleRead"},
                },
            },
            # -------------------------------------------------
            # RBAC - PERMISSIONS
            # -------------------------------------------------
            "PermissionRead": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"},
                    "resource": {"type": "string"},
                    "action": {"type": "string"},
                    "description": {"type": "string"},
                },
            },
            "PermissionWriteRequest": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "resource": {"type": "string"},
                    "action": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["name", "resource", "action"],
            },
            "PermissionPartialUpdateRequest": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "resource": {"type": "string"},
                    "action": {"type": "string"},
                    "description": {"type": "string"},
                },
            },
            "PermissionListResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/PermissionRead"},
                    },
                },
            },
            "PermissionDetailResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {"$ref": "#/components/schemas/PermissionRead"},
                },
            },
            # -------------------------------------------------
            # RBAC - USER ROLES
            # -------------------------------------------------
            "UserRoleRead": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "user": {"type": "string", "format": "uuid"},
                    "role": {"type": "string", "format": "uuid"},
                },
            },
            "UserRoleWriteRequest": {
                "type": "object",
                "properties": {
                    "user": {"type": "string", "format": "uuid"},
                    "role": {"type": "string", "format": "uuid"},
                },
                "required": ["user", "role"],
            },
            "UserRoleListResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/UserRoleRead"},
                    },
                },
            },
            "UserRoleDetailResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {"$ref": "#/components/schemas/UserRoleRead"},
                },
            },
            # -------------------------------------------------
            # RBAC - ROLE PERMISSIONS
            # -------------------------------------------------
            "RolePermissionRead": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "role": {"type": "string", "format": "uuid"},
                    "permission": {"type": "string", "format": "uuid"},
                },
            },
            "RolePermissionWriteRequest": {
                "type": "object",
                "properties": {
                    "role": {"type": "string", "format": "uuid"},
                    "permission": {"type": "string", "format": "uuid"},
                },
                "required": ["role", "permission"],
            },
            "RolePermissionListResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/RolePermissionRead"},
                    },
                },
            },
            "RolePermissionDetailResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "data": {"$ref": "#/components/schemas/RolePermissionRead"},
                },
            },
            # -------------------------------------------------
            # COMMON RESPONSES
            # -------------------------------------------------
            "SuccessMessageResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True},
                    "message": {"type": "string"},
                },
            },
            "HealthResponse": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "ok"},
                    "service": {"type": "string", "example": "identity"},
                },
                "required": ["status", "service"],
            },
            "ValidationErrorResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": False},
                    "message": {"type": "string", "example": "Validation error."},
                    "errors": {"type": "object", "additionalProperties": True},
                },
            },
            "NotFoundResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": False},
                    "message": {"type": "string"},
                },
            },
            "AuthenticationErrorResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": False},
                    "message": {"type": "string", "example": "Invalid credentials."},
                },
            },
        }
    # =========================================================
    # COMMON HELPERS
    # =========================================================

    def _uuid_parameter(self, name, description):
        return {
            "name": name,
            "in": "path",
            "required": True,
            "description": description,
            "schema": {"type": "string", "format": "uuid"},
        }

    def _user_id_parameter(self):
        return self._uuid_parameter("user_id", "UUID of the user.")

    def _request_body(self, schema_name):
        return {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {"$ref": f"#/components/schemas/{schema_name}"},
                },
            },
        }

    def _response(self, description, schema_name):
        return {
            "description": description,
            "content": {
                "application/json": {
                    "schema": {"$ref": f"#/components/schemas/{schema_name}"},
                },
            },
        }

    def _validation_response(self):
        return self._response("Invalid request data.", "ValidationErrorResponse")

    def _not_found_response(self):
        return self._response("Resource not found.", "NotFoundResponse")

    def _success_response(self, description):
        return self._response(description, "SuccessMessageResponse")
    # =========================================================
    # USERS PATHS
    # =========================================================

    def _health_path(self):
        return {
            "get": {
                "operationId": "identityHealthCheck",
                "summary": "Check identity service health",
                "tags": ["Identity"],
                "responses": {
                    "200": self._response(
                        "Identity service is available.",
                        "HealthResponse",
                    ),
                },
            },
        }

    def _register_path(self):
        return {
            "post": {
                "operationId": "registerUser",
                "summary": "Register a new Kora user",
                "tags": ["Users"],
                "requestBody": self._request_body("UserRegistrationRequest"),
                "responses": {
                    "201": self._response(
                        "User registered successfully.",
                        "UserRegistrationResponse",
                    ),
                    "400": self._validation_response(),
                },
            },
        }

    def _login_path(self):
        return {
            "post": {
                "operationId": "loginUser",
                "summary": "Authenticate a user and generate JWT tokens",
                "tags": ["Authentication"],
                "requestBody": self._request_body("UserLoginRequest"),
                "responses": {
                    "200": self._response(
                        "Login successful. JWT tokens generated.",
                        "UserLoginResponse",
                    ),
                    "400": self._validation_response(),
                    "401": self._response(
                        "Invalid credentials or inactive user.",
                        "AuthenticationErrorResponse",
                    ),
                },
            },
        }

    def _refresh_path(self):
        return {
            "post": {
                "operationId": "refreshAccessToken",
                "summary": "Generate a new access token",
                "tags": ["Authentication"],
                "requestBody": self._request_body("TokenRefreshRequest"),
                "responses": {
                    "200": self._response(
                        "Access token successfully renewed.",
                        "TokenRefreshResponse",
                    ),
                    "401": {"description": "Invalid or expired refresh token."},
                },
            },
        }

    def _users_path(self):
        return {
            "get": {
                "operationId": "listUsers",
                "summary": "List all active users",
                "tags": ["Users"],
                "responses": {
                    "200": self._response(
                        "Active users retrieved successfully.",
                        "UserListResponse",
                    ),
                },
            },
        }

    def _user_detail_path(self):
        return {
            "parameters": [self._user_id_parameter()],
            "get": {
                "operationId": "retrieveUser",
                "summary": "Retrieve an active user by ID",
                "tags": ["Users"],
                "responses": {
                    "200": self._response(
                        "User retrieved successfully.",
                        "UserDetailResponse",
                    ),
                    "404": self._not_found_response(),
                },
            },
            "delete": {
                "operationId": "deactivateUser",
                "summary": "Deactivate a user",
                "tags": ["Users"],
                "responses": {
                    "200": self._success_response("User deactivated successfully."),
                    "404": self._not_found_response(),
                },
            },
        }

    def _user_update_path(self):
        return {
            "parameters": [self._user_id_parameter()],
            "put": {
                "operationId": "updateUser",
                "summary": "Update user information",
                "tags": ["Users"],
                "requestBody": self._request_body("UserUpdateRequest"),
                "responses": {
                    "200": self._response(
                        "User updated successfully.",
                        "UserUpdateResponse",
                    ),
                    "400": self._validation_response(),
                    "404": self._not_found_response(),
                },
            },
            "patch": {
                "operationId": "partialUpdateUser",
                "summary": "Partially update user information",
                "tags": ["Users"],
                "requestBody": self._request_body("UserPartialUpdateRequest"),
                "responses": {
                    "200": self._response(
                        "User updated successfully.",
                        "UserUpdateResponse",
                    ),
                    "400": self._validation_response(),
                    "404": self._not_found_response(),
                },
            },
        }
    # =========================================================
    # RBAC - ROLES PATHS
    # =========================================================

    def _roles_path(self):
        return {
            "get": {
                "operationId": "listRoles",
                "summary": "List all roles",
                "tags": ["RBAC - Roles"],
                "responses": {
                    "200": self._response(
                        "Roles retrieved successfully.",
                        "RoleListResponse",
                    ),
                },
            },
            "post": {
                "operationId": "createRole",
                "summary": "Create a new role",
                "tags": ["RBAC - Roles"],
                "requestBody": self._request_body("RoleWriteRequest"),
                "responses": {
                    "201": self._response(
                        "Role created successfully.",
                        "RoleDetailResponse",
                    ),
                    "400": self._validation_response(),
                },
            },
        }

    def _role_detail_path(self):
        return {
            "parameters": [self._uuid_parameter("role_id", "UUID of the role.")],
            "get": {
                "operationId": "retrieveRole",
                "summary": "Retrieve a role by ID",
                "tags": ["RBAC - Roles"],
                "responses": {
                    "200": self._response(
                        "Role retrieved successfully.",
                        "RoleDetailResponse",
                    ),
                    "404": self._not_found_response(),
                },
            },
            "put": {
                "operationId": "updateRole",
                "summary": "Update a role",
                "tags": ["RBAC - Roles"],
                "requestBody": self._request_body("RoleWriteRequest"),
                "responses": {
                    "200": self._response(
                        "Role updated successfully.",
                        "RoleDetailResponse",
                    ),
                    "400": self._validation_response(),
                    "404": self._not_found_response(),
                },
            },
            "patch": {
                "operationId": "partialUpdateRole",
                "summary": "Partially update a role",
                "tags": ["RBAC - Roles"],
                "requestBody": self._request_body("RolePartialUpdateRequest"),
                "responses": {
                    "200": self._response(
                        "Role updated successfully.",
                        "RoleDetailResponse",
                    ),
                    "400": self._validation_response(),
                    "404": self._not_found_response(),
                },
            },
            "delete": {
                "operationId": "deleteRole",
                "summary": "Delete a role",
                "tags": ["RBAC - Roles"],
                "responses": {
                    "200": self._success_response("Role deleted successfully."),
                    "404": self._not_found_response(),
                },
            },
        }
    # =========================================================
    # RBAC - PERMISSIONS PATHS
    # =========================================================

    def _permissions_path(self):
        return {
            "get": {
                "operationId": "listPermissions",
                "summary": "List all permissions",
                "tags": ["RBAC - Permissions"],
                "responses": {
                    "200": self._response(
                        "Permissions retrieved successfully.",
                        "PermissionListResponse",
                    ),
                },
            },
            "post": {
                "operationId": "createPermission",
                "summary": "Create a new permission",
                "tags": ["RBAC - Permissions"],
                "requestBody": self._request_body("PermissionWriteRequest"),
                "responses": {
                    "201": self._response(
                        "Permission created successfully.",
                        "PermissionDetailResponse",
                    ),
                    "400": self._validation_response(),
                },
            },
        }

    def _permission_detail_path(self):
        return {
            "parameters": [
                self._uuid_parameter(
                    "permission_id", "UUID of the permission."),
            ],
            "get": {
                "operationId": "retrievePermission",
                "summary": "Retrieve a permission by ID",
                "tags": ["RBAC - Permissions"],
                "responses": {
                    "200": self._response(
                        "Permission retrieved successfully.",
                        "PermissionDetailResponse",
                    ),
                    "404": self._not_found_response(),
                },
            },
            "put": {
                "operationId": "updatePermission",
                "summary": "Update a permission",
                "tags": ["RBAC - Permissions"],
                "requestBody": self._request_body("PermissionWriteRequest"),
                "responses": {
                    "200": self._response(
                        "Permission updated successfully.",
                        "PermissionDetailResponse",
                    ),
                    "400": self._validation_response(),
                    "404": self._not_found_response(),
                },
            },
            "patch": {
                "operationId": "partialUpdatePermission",
                "summary": "Partially update a permission",
                "tags": ["RBAC - Permissions"],
                "requestBody": self._request_body("PermissionPartialUpdateRequest"),
                "responses": {
                    "200": self._response(
                        "Permission updated successfully.",
                        "PermissionDetailResponse",
                    ),
                    "400": self._validation_response(),
                    "404": self._not_found_response(),
                },
            },
            "delete": {
                "operationId": "deletePermission",
                "summary": "Delete a permission",
                "tags": ["RBAC - Permissions"],
                "responses": {
                    "200": self._success_response("Permission deleted successfully."),
                    "404": self._not_found_response(),
                },
            },
        }
    # =========================================================
    # RBAC - USER ROLES PATHS
    # =========================================================

    def _user_roles_path(self):
        return {
            "get": {
                "operationId": "listUserRoles",
                "summary": "List user-role assignments",
                "tags": ["RBAC - User Roles"],
                "responses": {
                    "200": self._response(
                        "User-role assignments retrieved successfully.",
                        "UserRoleListResponse",
                    ),
                },
            },
            "post": {
                "operationId": "assignRoleToUser",
                "summary": "Assign a role to a user",
                "tags": ["RBAC - User Roles"],
                "requestBody": self._request_body("UserRoleWriteRequest"),
                "responses": {
                    "201": self._response(
                        "Role assigned to user successfully.",
                        "UserRoleDetailResponse",
                    ),
                    "400": self._validation_response(),
                },
            },
        }

    def _user_role_detail_path(self):
        return {
            "parameters": [
                self._uuid_parameter(
                    "user_role_id",
                    "UUID of the user-role assignment.",
                ),
            ],
            "get": {
                "operationId": "retrieveUserRole",
                "summary": "Retrieve a user-role assignment",
                "tags": ["RBAC - User Roles"],
                "responses": {
                    "200": self._response(
                        "User-role assignment retrieved successfully.",
                        "UserRoleDetailResponse",
                    ),
                    "404": self._not_found_response(),
                },
            },
            "delete": {
                "operationId": "removeUserRole",
                "summary": "Remove a role from a user",
                "tags": ["RBAC - User Roles"],
                "responses": {
                    "200": self._success_response(
                        "User-role assignment deleted successfully.",
                    ),
                    "404": self._not_found_response(),
                },
            },
        }
    # =========================================================
    # RBAC - ROLE PERMISSIONS PATHS
    # =========================================================

    def _role_permissions_path(self):
        return {
            "get": {
                "operationId": "listRolePermissions",
                "summary": "List role-permission assignments",
                "tags": ["RBAC - Role Permissions"],
                "responses": {
                    "200": self._response(
                        "Role-permission assignments retrieved successfully.",
                        "RolePermissionListResponse",
                    ),
                },
            },
            "post": {
                "operationId": "assignPermissionToRole",
                "summary": "Assign a permission to a role",
                "tags": ["RBAC - Role Permissions"],
                "requestBody": self._request_body("RolePermissionWriteRequest"),
                "responses": {
                    "201": self._response(
                        "Permission assigned to role successfully.",
                        "RolePermissionDetailResponse",
                    ),
                    "400": self._validation_response(),
                },
            },
        }

    def _role_permission_detail_path(self):
        return {
            "parameters": [
                self._uuid_parameter(
                    "role_permission_id",
                    "UUID of the role-permission assignment.",
                ),
            ],
            "get": {
                "operationId": "retrieveRolePermission",
                "summary": "Retrieve a role-permission assignment",
                "tags": ["RBAC - Role Permissions"],
                "responses": {
                    "200": self._response(
                        "Role-permission assignment retrieved successfully.",
                        "RolePermissionDetailResponse",
                    ),
                    "404": self._not_found_response(),
                },
            },
            "delete": {
                "operationId": "removeRolePermission",
                "summary": "Remove a permission from a role",
                "tags": ["RBAC - Role Permissions"],
                "responses": {
                    "200": self._success_response(
                        "Role-permission assignment deleted successfully.",
                    ),
                    "404": self._not_found_response(),
                },
            },
        }
