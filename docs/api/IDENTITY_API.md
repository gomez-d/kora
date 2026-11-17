# Kora Identity Service — API Contract

## 1. Overview

The Identity Service is responsible for user identity management and Role-Based Access Control (RBAC).

It is organized into two Django applications:

- **Users:** Handles user registration, authentication, profile management, and account deactivation.
- **RBAC:** Handles roles, permissions, and the relationships between users, roles, and permissions.

Both applications are exposed through the Identity Service API.

### Base URL

```text
/api/
```

### Response Format

API responses follow a consistent JSON structure.

**Successful response:**

```json
{
  "success": true,
  "data": {}
}
```

**Successful operation with a message:**

```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": {}
}
```

**Error response:**

```json
{
  "success": false,
  "message": "An error occurred.",
  "errors": {}
}
```

The `errors` property is included when additional validation details are available.

---

# 2. Users API

The Users application manages user accounts and authentication.

## 2.1 Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/users/health/` | Check service availability |
| POST | `/api/users/register/` | Register a new user |
| GET | `/api/users/users/` | Retrieve active users |
| GET | `/api/users/users/{user_id}/` | Retrieve a specific active user |
| PUT | `/api/users/users/{user_id}/update/` | Replace user information |
| PATCH | `/api/users/users/{user_id}/update/` | Partially update user information |
| DELETE | `/api/users/users/{user_id}/` | Deactivate a user |
| POST | `/api/users/login/` | Authenticate a user |
| POST | `/api/users/token/refresh/` | Refresh an access token |

`{user_id}` is a UUID identifying the user.

## 2.2 Health Check

### GET `/api/users/health/`

Checks whether the Identity Service is available.

**Response:**

Returns the health-check response implemented by the service.

## 2.3 User Registration

### POST `/api/users/register/`

Creates a new user account.

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1995-05-20"
}
```

**Fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| email | string | Yes | Unique user email address |
| password | string | Yes | User password |
| first_name | string | Yes | User's first name |
| last_name | string | Yes | User's last name |
| date_of_birth | date | Yes | User's date of birth |

**Validation rules:**

- Email addresses must be unique.
- Passwords must comply with Django password validators.
- Date of birth cannot be in the future.
- Date of birth cannot be null during registration.

**Successful response:**

Returns the created user's information, including the generated `user_id`.

The password is never returned.

## 2.4 Retrieve All Users

### GET `/api/users/users/`

Retrieves the list of active users.

**Request body:** None.

**Successful response:**

```json
{
  "success": true,
  "data": [
    {
      "user_id": "UUID",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "date_of_birth": "1995-05-20"
    }
  ]
}
```

Inactive users are excluded from the results.

## 2.5 Retrieve a User

### GET `/api/users/users/{user_id}/`

Retrieves an individual active user.

**Path parameter:**

| Parameter | Type | Description |
|---|---|---|
| user_id | UUID | Unique identifier of the user |

**Request body:** None.

**Successful response:**

```json
{
  "success": true,
  "data": {
    "user_id": "UUID",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1995-05-20"
  }
}
```

Returns `404 Not Found` if the user does not exist or is inactive.

## 2.6 Update a User

### PUT `/api/users/users/{user_id}/update/`

Replaces the editable user information.

**Request body:**

```json
{
  "email": "newemail@example.com",
  "first_name": "John",
  "last_name": "Smith",
  "date_of_birth": "1995-05-20"
}
```

All fields must be provided according to the update serializer's validation rules.

### PATCH `/api/users/users/{user_id}/update/`

Partially updates the editable user information.

**Example request body:**

```json
{
  "first_name": "Jonathan"
}
```

Only the supplied fields are updated.

**Editable fields:**

| Field | Type |
|---|---|
| email | string |
| first_name | string |
| last_name | string |
| date_of_birth | date |

**Validation rules:**

- Email addresses must remain unique.
- Date of birth cannot be in the future.
- The user must exist and be active.

Both operations return the updated user information on success.

## 2.7 Deactivate a User

### DELETE `/api/users/users/{user_id}/`

Deactivates an existing user account.

This operation performs a **soft deactivation**. The user record is not physically deleted from the database.

**Request body:** None.

**Successful response:**

Returns a success response with a confirmation message.

**Expected behavior:**

- The user's `is_active` field is set to `false`.
- Inactive users are excluded from user listings.
- Inactive users cannot be retrieved through the individual user endpoint.
- Inactive users cannot authenticate.

Returns `404 Not Found` if the user does not exist.

## 2.8 User Login

### POST `/api/users/login/`

Authenticates a user using email and password.

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

**Successful response:**

```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "user_id": "UUID",
    "access": "ACCESS_TOKEN",
    "refresh": "REFRESH_TOKEN"
  }
}
```

**Authentication behavior:**

- Credentials are validated using Django authentication.
- Inactive users cannot log in.
- Successful authentication returns JWT access and refresh tokens.

Invalid credentials return an authentication error.

## 2.9 Refresh Access Token

### POST `/api/users/token/refresh/`

Generates a new access token using a valid refresh token.

**Request body:**

```json
{
  "refresh": "REFRESH_TOKEN"
}
```

**Successful response:**

```json
{
  "access": "NEW_ACCESS_TOKEN"
}
```

This endpoint uses the SimpleJWT token refresh implementation.

---

# 3. RBAC API

The RBAC application implements Role-Based Access Control.

It manages four main resources:

- **Roles:** Define groups of access permissions.
- **Permissions:** Define available system permissions.
- **User Roles:** Associate users with roles.
- **Role Permissions:** Associate permissions with roles.

## 3.1 Endpoints Overview

| Resource | Method | Endpoint | Description |
|---|---|---|---|
| Roles | GET | `/api/rbac/roles/` | List roles |
| Roles | POST | `/api/rbac/roles/` | Create a role |
| Roles | GET | `/api/rbac/roles/{role_id}/` | Retrieve a role |
| Roles | PUT | `/api/rbac/roles/{role_id}/` | Replace a role |
| Roles | PATCH | `/api/rbac/roles/{role_id}/` | Partially update a role |
| Roles | DELETE | `/api/rbac/roles/{role_id}/` | Delete a role |
| Permissions | GET | `/api/rbac/permissions/` | List permissions |
| Permissions | POST | `/api/rbac/permissions/` | Create a permission |
| Permissions | GET | `/api/rbac/permissions/{permission_id}/` | Retrieve a permission |
| Permissions | PUT | `/api/rbac/permissions/{permission_id}/` | Replace a permission |
| Permissions | PATCH | `/api/rbac/permissions/{permission_id}/` | Partially update a permission |
| Permissions | DELETE | `/api/rbac/permissions/{permission_id}/` | Delete a permission |
| User Roles | GET | `/api/rbac/user-roles/` | List user-role assignments |
| User Roles | POST | `/api/rbac/user-roles/` | Assign a role to a user |
| User Roles | GET | `/api/rbac/user-roles/{user_role_id}/` | Retrieve an assignment |
| User Roles | DELETE | `/api/rbac/user-roles/{user_role_id}/` | Remove an assignment |
| Role Permissions | GET | `/api/rbac/role-permissions/` | List role-permission assignments |
| Role Permissions | POST | `/api/rbac/role-permissions/` | Assign a permission to a role |
| Role Permissions | GET | `/api/rbac/role-permissions/{role_permission_id}/` | Retrieve an assignment |
| Role Permissions | DELETE | `/api/rbac/role-permissions/{role_permission_id}/` | Remove an assignment |

All resource identifiers are UUIDs.

## 3.2 Roles

Roles represent groups of permissions that can be assigned to users.

### GET `/api/rbac/roles/`

Retrieves all roles.

**Request body:** None.

**Successful response:**

Returns a collection of roles using the role read serializer. The response includes the role's associated permissions.

### POST `/api/rbac/roles/`

Creates a new role.

**Request body:**

Uses the fields defined by `RoleWriteSerializer`.

### GET `/api/rbac/roles/{role_id}/`

Retrieves a specific role, including its associated permissions.

### PUT `/api/rbac/roles/{role_id}/`

Replaces the role's editable information.

**Request body:** Complete role data according to `RoleWriteSerializer`.

### PATCH `/api/rbac/roles/{role_id}/`

Partially updates a role.

**Request body:** Only the fields to be updated, according to `RoleWriteSerializer`.

### DELETE `/api/rbac/roles/{role_id}/`

Deletes the specified role.

**Request body:** None.

Successful deletion returns a confirmation message.

## 3.3 Permissions

Permissions represent individual access capabilities.

A permission is described by its name, resource, and action.

### GET `/api/rbac/permissions/`

Retrieves all registered permissions.

**Request body:** None.

### POST `/api/rbac/permissions/`

Creates a permission.

**Request body:**

```json
{
  "name": "View Users",
  "resource": "users",
  "action": "read"
}
```

### GET `/api/rbac/permissions/{permission_id}/`

Retrieves a specific permission.

### PUT `/api/rbac/permissions/{permission_id}/`

Replaces the permission's editable information.

**Request body:**

```json
{
  "name": "Update Users",
  "resource": "users",
  "action": "update"
}
```

### PATCH `/api/rbac/permissions/{permission_id}/`

Partially updates a permission.

**Example request body:**

```json
{
  "action": "delete"
}
```

### DELETE `/api/rbac/permissions/{permission_id}/`

Deletes the specified permission.

**Request body:** None.

Successful deletion returns a confirmation message.

## 3.4 User Roles

User Roles represent the relationship between a user and a role.

This resource allows the system to assign and remove roles from users.

### GET `/api/rbac/user-roles/`

Retrieves all user-role assignments.

### POST `/api/rbac/user-roles/`

Assigns a role to a user.

**Request body:**

```json
{
  "user": "USER_UUID",
  "role": "ROLE_UUID"
}
```

Both identifiers must reference existing records.

### GET `/api/rbac/user-roles/{user_role_id}/`

Retrieves a specific user-role assignment.

### DELETE `/api/rbac/user-roles/{user_role_id}/`

Removes a role assignment from a user.

This operation deletes the relationship, not the user or the role.

## 3.5 Role Permissions

Role Permissions represent the relationship between a role and a permission.

This resource allows permissions to be assigned to or removed from roles.

### GET `/api/rbac/role-permissions/`

Retrieves all role-permission assignments.

### POST `/api/rbac/role-permissions/`

Assigns a permission to a role.

**Request body:**

```json
{
  "role": "ROLE_UUID",
  "permission": "PERMISSION_UUID"
}
```

Both identifiers must reference existing records.

### GET `/api/rbac/role-permissions/{role_permission_id}/`

Retrieves a specific role-permission assignment.

### DELETE `/api/rbac/role-permissions/{role_permission_id}/`

Removes a permission assignment from a role.

This operation deletes the relationship, not the role or the permission.

---

# 4. HTTP Status Codes

The API uses standard HTTP status codes to communicate operation results.

| Status Code | Meaning |
|---|---|
| 200 OK | Request completed successfully |
| 201 Created | Resource successfully created |
| 204 No Content | Successful operation without a response body, when applicable |
| 400 Bad Request | Invalid request data or validation error |
| 401 Unauthorized | Authentication failed or credentials are invalid |
| 404 Not Found | Requested resource does not exist or is unavailable |

The exact response status depends on the endpoint and operation.

---

# 5. OpenAPI Documentation

The Identity Service exposes a unified OpenAPI schema for both Users and RBAC.

### GET `/api/schema/`

Returns the OpenAPI specification describing the Identity Service API.

The schema includes:

- Users endpoints.
- RBAC endpoints.
- HTTP operations.
- Request schemas.
- Response schemas.
- Data types and UUID formats.
- Relevant error responses.

The schema is generated through the custom `IdentitySchemaGenerator`, located in:

```text
api_docs/openapi.py
```

The documentation is centralized at the service level because Users and RBAC belong to the same Identity microservice.

---

# 6. Resource and Relationship Overview

The RBAC data model establishes the following relationships:

```text
User
  |
  | UserRole
  |
Role
  |
  | RolePermission
  |
Permission
```

- A user can have multiple roles.
- A role can be assigned to multiple users.
- A role can contain multiple permissions.
- A permission can belong to multiple roles.

The relationships are managed through the `UserRole` and `RolePermission` models.

---

# 7. API Scope

The Identity Service currently provides:

- User registration and authentication.
- User listing and individual retrieval.
- User profile updates.
- User account deactivation.
- JWT access token generation and refresh.
- Role management.
- Permission management.
- User-role assignments.
- Role-permission assignments.
- Unified OpenAPI documentation.

The API contract described here reflects the implemented Users and RBAC endpoints.