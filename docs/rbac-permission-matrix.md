# Kora RBAC Permission Matrix

## Overview

Kora uses role-based access control (RBAC) to protect operations in the Identity and Business services.

The current system roles are:

- `USER`
- `ADMIN`

Permissions follow the naming convention:

```text
<resource>.<action>
```

Self-scoped permissions use actions ending in:

```text
_self
```

Administrative permissions that allow operations over other users use actions ending in:

```text
_any
```

---

## Identity Permissions

| Permission                | Resource          | Action            | USER  | ADMIN | Description                                       |
|---------------------------|-------------------|-------------------|-------|-------|---------------------------------------------------|
| `users.read_self`         | users             | read_self         | Yes   | Yes   | Read the authenticated user's own information     |
| `users.update_self`       | users             | update_self       | Yes   | Yes   | Update the authenticated user's own information   |
| `users.deactivate_self`   | users             | deactivate_self   | Yes   | Yes   | Deactivate the authenticated user's own account   |
| `users.read_any`          | users             | read_any          | No    | Yes   | Read information from any user                    |
| `users.deactivate_any`    | users             | deactivate_any    | No    | Yes   | Deactivate any user account                       |
| `user_roles.read_self`    | user_roles        | read_self         | Yes   | Yes   | Read the authenticated user's role assignments    |
| `user_roles.read_any`     | user_roles        | read_any          | No    | Yes   | Read role assignments for any user                |
| `user_roles.assign`       | user_roles        | assign            | No    | Yes   | Assign a role to a user                           |
| `user_roles.remove`       | user_roles        | remove            | No    | Yes   | Remove a role assignment from a user              |
| `roles.read`              | roles             | read              | No    | Yes   | Read available roles                              |
| `roles.create`            | roles             | create            | No    | Yes   | Create roles                                      |
| `roles.update`            | roles             | update            | No    | Yes   | Update roles                                      |
| `roles.delete`            | roles             | delete            | No    | Yes   | Delete roles                                      |
| `permissions.read`        | permissions       | read              | No    | Yes   | Read available permissions                        |
| `permissions.create`      | permissions       | create            | No    | Yes   | Create permissions                                |
| `permissions.update`      | permissions       | update            | No    | Yes   | Update permissions                                |
| `permissions.delete`      | permissions       | delete            | No    | Yes   | Delete permissions                                |
| `role_permissions.read`   | role_permissions  | read              | No    | Yes   | Read role-permission assignments                  |
| `role_permissions.assign` | role_permissions  | assign            | No    | Yes   | Assign a permission to a role                     |
| `role_permissions.remove` | role_permissions  | remove            | No    | Yes   | Remove a permission from a role                   |

---

## Business Permissions

| Permission                            | Resource              | Action        | USER  | ADMIN | Description                                             |
|---------------------------------------|-----------------------|---------------|-------|-------|---------------------------------------------------------|
| `foods.read`                          | foods                 | read          | Yes   | Yes   | Read the food catalog                                   |     
| `foods.create`                        | foods                 | create        | No    | Yes   | Create food catalog entries                             |
| `foods.update`                        | foods                 | update        | No    | Yes   | Update food catalog entries                             |
| `foods.delete`                        | foods                 | delete        | No    | Yes   | Delete food catalog entries                             |
| `food_categories.read`                | food_categories       | read          | Yes   | Yes   | Read food categories                                    |
| `food_categories.create`              | food_categories       | create        | No    | Yes   | Create food categories                                  |
| `nutritional_profiles.read_self`      | nutritional_profiles  | read_self     | Yes   | Yes   | Read the authenticated user's nutritional profile       |
| `nutritional_profiles.create_self`    | nutritional_profiles  | create_self   | Yes   | Yes   | Create the authenticated user's nutritional profile     |
| `nutritional_profiles.update_self`    | nutritional_profiles  | update_self   | Yes   | Yes   | Update the authenticated user's nutritional profile     |
| `consumptions.read_self`              | consumptions          | read_self     | Yes   | Yes   | Read the authenticated user's consumption records       |
| `consumptions.create_self`            | consumptions          | create_self   | Yes   | Yes   | Create consumption records for the authenticated user   |
| `consumptions.update_self`            | consumptions          | update_self   | Yes   | Yes   | Update the authenticated user's consumption records     |

---

## Identity Endpoint Authorization Matrix

| Endpoint                                              | Method    | Access                            | Required Permission                               |
|-------------------------------------------------------|-----------|-----------------------------------|---------------------------------------------------|
| `/api/users/health/`                                  | GET       | Public                            | None                                              |
| `/api/users/register/`                                | POST      | Public                            | None                                              |
| `/api/users/login/`                                   | POST      | Public                            | None                                              |
| `/api/users/token/refresh/`                           | POST      | Public with valid refresh token   | None                                              |
| `/api/users/users/`                                   | GET       | Administrative                    | `users.read_any`                                  |
| `/api/users/users/{user_id}/`                         | GET       | Self / Administrative             | `users.read_self` or `users.read_any`             |
| `/api/users/users/{user_id}/`                         | DELETE    | Self / Administrative             | `users.deactivate_self` or `users.deactivate_any` |
| `/api/users/users/{user_id}/update/`                  | PUT       | Self                              | `users.update_self`                               |
| `/api/users/users/{user_id}/update/`                  | PATCH     | Self                              | `users.update_self`                               |
| `/api/rbac/roles/`                                    | GET       | Administrative                    | `roles.read`                                      |
| `/api/rbac/roles/`                                    | POST      | Administrative                    | `roles.create`                                    |
| `/api/rbac/roles/{role_id}/`                          | GET       | Administrative                    | `roles.read`                                      |
| `/api/rbac/roles/{role_id}/`                          | PUT       | Administrative                    | `roles.update`                                    |
| `/api/rbac/roles/{role_id}/`                          | PATCH     | Administrative                    | `roles.update`                                    |
| `/api/rbac/roles/{role_id}/`                          | DELETE    | Administrative                    | `roles.delete`                                    |
| `/api/rbac/permissions/`                              | GET       | Administrative                    | `permissions.read`                                |
| `/api/rbac/permissions/`                              | POST      | Administrative                    | `permissions.create`                              |
| `/api/rbac/permissions/{permission_id}/`              | GET       | Administrative                    | `permissions.read`                                |
| `/api/rbac/permissions/{permission_id}/`              | PUT       | Administrative                    | `permissions.update`                              |
| `/api/rbac/permissions/{permission_id}/`              | PATCH     | Administrative                    | `permissions.update`                              |
| `/api/rbac/permissions/{permission_id}/`              | DELETE    | Administrative                    | `permissions.delete`                              |
| `/api/rbac/user-roles/`                               | GET       | Administrative                    | `user_roles.read_any`                             |
| `/api/rbac/user-roles/`                               | POST      | Administrative                    | `user_roles.assign`                               |
| `/api/rbac/user-roles/{user_role_id}/`                | GET       | Administrative                    | `user_roles.read_any`                             |
| `/api/rbac/user-roles/{user_role_id}/`                | DELETE    | Administrative                    | `user_roles.remove`                               |
| `/api/rbac/role-permissions/`                         | GET       | Administrative                    | `role_permissions.read`                           |
| `/api/rbac/role-permissions/`                         | POST      | Administrative                    | `role_permissions.assign`                         |
| `/api/rbac/role-permissions/{role_permission_id}/`    | GET       | Administrative                    | `role_permissions.read`                           |
| `/api/rbac/role-permissions/{role_permission_id}/`    | DELETE    | Administrative                    | `role_permissions.remove`                         |

---

## Business Endpoint Authorization Matrix

| Endpoint                                  | Method    | Access            | Required Permission                   |
|-------------------------------------------|-----------|-------------------|---------------------------------------|
| `/api/health/`                            | GET       | Public            | None                                  |
| `/api/food-categories/`                   | GET       | Authenticated     | `food_categories.read`                |
| `/api/food-categories/`                   | POST      | Administrative    | `food_categories.create`              |
| `/api/foods/`                             | GET       | Authenticated     | `foods.read`                          |
| `/api/foods/`                             | POST      | Administrative    | `foods.create`                        |
| `/api/foods/{food_id}/`                   | GET       | Authenticated     | `foods.read`                          |
| `/api/foods/{food_id}/`                   | PUT       | Administrative    | `foods.update`                        |
| `/api/foods/{food_id}/`                   | PATCH     | Administrative    | `foods.update`                        |
| `/api/foods/{food_id}/`                   | DELETE    | Administrative    | `foods.delete`                        |
| `/api/nutritional-profiles/`              | GET       | Self              | `nutritional_profiles.read_self`      |
| `/api/nutritional-profiles/`              | POST      | Self              | `nutritional_profiles.create_self`    |
| `/api/nutritional-profiles/{profile_id}/` | PATCH     | Self              | `nutritional_profiles.update_self`    |
| `/api/consumptions/`                      | GET       | Self              | `consumptions.read_self`              |
| `/api/consumptions/`                      | POST      | Self              | `consumptions.create_self`            |
| `/api/consumptions/{consumption_id}/`     | PATCH     | Self              | `consumptions.update_self`            |

---

## Authentication and Authorization Responses

Protected endpoints use the following response rules.

### 401 Unauthorized

Returned when the request does not establish a valid authenticated identity.

Examples:

- Missing authentication token.
- Invalid authentication token.
- Expired authentication token.
- Malformed authentication credentials.

Response:

```json
{
  "success": false,
  "code": "unauthorized",
  "message": "Authentication credentials are missing or invalid."
}
```

---

### 403 Forbidden

Returned when the request contains a valid authenticated identity but the user does not have the required permission or does not own the requested resource.

Examples:

- A `USER` attempts an administrative operation.
- The required RBAC permission is missing.
- A user attempts to access another user's private resource.

Response:

```json
{
  "success": false,
  "code": "forbidden",
  "message": "You do not have permission to perform this operation."
}
```

---

## Ownership Rules

Self-scoped permissions only authorize operations over resources associated with the authenticated identity.

For existing resources, ownership is verified using:

```text
persisted resource.user_id
==
authenticated user_id
```

The client cannot bypass ownership validation by submitting another `user_id` in the request.

Ownership violations return:

```text
403 Forbidden
```

---

## JWT Authorization Context

Kora access tokens include the authorization context of the authenticated user.

The relevant claims are:

```text
user_id
roles
permissions
```

The Business service validates the JWT and uses these claims to authorize protected operations.

The Identity service uses the authenticated user and the RBAC relationships stored in PostgreSQL.

When a refresh token is used, the Identity service recalculates the current roles and permissions before issuing the new access token.

---

## Authorization Model Summary

The final authorization model follows these rules:

```text
Public endpoint
→ No access token required

Authenticated endpoint
→ Valid access token + required permission

Self-scoped endpoint
→ Valid access token + required self permission + ownership validation

Administrative endpoint
→ Valid access token + required administrative permission
```