# Kora System Roles

## Purpose

This document defines the roles currently available in Kora, their general responsibilities, and the rules used to assign, consult, and modify them.

The role model defined here serves as the foundation for implementing operation-specific permissions in future authorization rules.

---

## Available Roles

Kora currently defines two minimum system roles:

```text
USER
ADMIN
```

Roles are persisted in the Identity service database and associated with users through the RBAC model.

A user may have one or more roles through the `UserRole` relationship.

---

## USER Role

### Description

`USER` represents a standard Kora platform user.

This is the default role assigned to users who register through the public registration flow.

### General Responsibilities

A user with the `USER` role may perform operations intended for regular platform users, according to the authorization rules of each service.

Examples include:

- accessing their own platform functionality;
- consulting their own identity-related information when authorized;
- consulting their own assigned roles;
- using platform functionality available to standard users.

### Restrictions

A standard user cannot:

- assign roles to themselves;
- assign roles to other users;
- remove their own role;
- remove roles from other users;
- request the `ADMIN` role during registration;
- submit `role` or `roles` fields to control their initial role;
- consult another user's roles through the authorized role-consultation mechanism.

The specific resources available to `USER` will be defined through operation-level permissions.

---

## ADMIN Role

### Description

`ADMIN` represents an authorized Kora administrator.

This role is intended for administrative operations that require broader authorization than those available to standard users.

### General Responsibilities

An administrator may perform authorized administrative operations such as:

- consulting roles assigned to other users;
- assigning roles to users;
- removing user-role associations;
- using protected RBAC management mechanisms.

### Scope

The `ADMIN` role does not automatically imply unrestricted access to every resource in Kora.

Access to specific business operations must still be defined through explicit authorization and permission rules.

This distinction is important because role membership identifies the user's general capability level, while individual permissions determine access to specific operations.

---

## Initial Role Assignment

The public registration process assigns the `USER` role automatically.

The assignment follows this flow:

```text
Registration request
        ↓
Validate user data
        ↓
Reject client-provided role information
        ↓
Create user
        ↓
Assign USER role
        ↓
Complete registration
```

The initial role is controlled entirely by the Identity service.

Clients cannot select their initial role.

The following fields are rejected during registration:

```text
role
roles
```

Therefore, a client cannot obtain administrative privileges by sending:

```json
{
  "role": "ADMIN"
}
```

or:

```json
{
  "roles": ["ADMIN"]
}
```

---

## Role Persistence

Roles and user-role associations are persisted in PostgreSQL.

The current RBAC structure includes:

```text
User
Role
UserRole
Permission
RolePermission
```

The relationship between users and roles is implemented through `UserRole`.

Conceptually:

```text
User
  ↓
UserRole
  ↓
Role
```

A database constraint prevents duplicate associations between the same user and role.

---

## Role Consultation

Role information is exposed through a controlled, read-only mechanism.

The authorized endpoint is:

```text
GET /api/rbac/users/<user_id>/roles/
```

### Authorization Rules

A standard user may consult their own roles.

```text
USER → own roles → allowed
```

A standard user may not consult another user's roles.

```text
USER → another user's roles → denied
```

An administrator may consult another user's roles.

```text
ADMIN → another user's roles → allowed
```

Unauthenticated requests are rejected.

### Data Exposure

The role-consultation response exposes only the minimum information required for authorization decisions.

Example:

```json
{
  "user_id": "uuid",
  "roles": [
    "USER"
  ]
}
```

The endpoint does not expose unnecessary identity information such as:

```text
email
first_name
last_name
date_of_birth
password
```

---

## Role Modification

User-role modifications are restricted to authorized administrators.

The protected operations include role assignment and role removal.

### Assignment

```text
POST /api/rbac/user-roles/
```

Authorization:

```text
ADMIN → allowed
USER → denied
Unauthenticated → denied
```

### Removal

```text
DELETE /api/rbac/user-roles/<user_role_id>/
```

Authorization:

```text
ADMIN → allowed
USER → denied
Unauthenticated → denied
```

A standard user therefore cannot modify their own role or the roles assigned to another user.

---

## Identity Context

Role information is also incorporated into the signed JWT identity context.

An access token may contain:

```json
{
  "user_id": "uuid",
  "roles": [
    "USER"
  ]
}
```

The `roles` claim is generated by the Identity service using the user's persisted role associations.

It is not obtained from client-provided data.

This allows authorization components to use a signed identity context instead of trusting role information supplied by the client.

---

## Token Refresh and Role Changes

When an access token is refreshed, the user's current roles are retrieved again from PostgreSQL.

This ensures that role changes are reflected in subsequently generated access tokens.

Example:

```text
Initial role:
USER

Role changed in PostgreSQL:
USER + ADMIN

Existing refresh token is used
        ↓
Current roles are retrieved
        ↓
New access token:
USER + ADMIN
```

The same applies when privileges are removed.

This prevents outdated role information from being propagated indefinitely through token refresh operations.

Inactive users cannot obtain new access tokens through the refresh mechanism.

---

## Role Management Rules

The current role-management rules are summarized below:

| Rule | USER | ADMIN |
|---|---|---|
| Receive `USER` during normal registration | Yes | N/A |
| Select role during registration | No | No |
| Consult own roles | Yes | Yes |
| Consult another user's roles | No | Yes |
| Assign roles | No | Yes |
| Remove roles | No | Yes |
| Modify own roles through RBAC endpoints | No | Authorized by administrative role |
| Modify another user's roles | No | Yes |

Administrative capabilities remain subject to future operation-specific permission rules.

---

## Security Principles

The role implementation follows these principles:

1. Role information is managed by the Identity service.
2. Role assignments are persisted in PostgreSQL.
3. Public registration never accepts client-controlled role assignment.
4. Standard users cannot modify user-role associations.
5. Administrative operations require authenticated `ADMIN` access.
6. Role consultation exposes only the minimum required information.
7. JWT role claims are generated from server-side identity data.
8. Role changes are reflected during token refresh.
9. Role membership does not automatically grant unrestricted access to all system resources.

---

## Future Permission Model

Roles define broad user categories.

The next authorization layer should define specific permissions associated with operations or resources.

The existing RBAC structure already supports:

```text
Role
Permission
RolePermission
```

This allows future authorization rules to evolve toward:

```text
User
  ↓
Role
  ↓
Permission
  ↓
Allowed operation
```

Examples of future permissions may include operations such as:

```text
users.read
users.manage
foods.read
foods.manage
consumptions.create
recommendations.read
```

The exact permission catalog must be defined from the functional requirements of each Kora module and should not be inferred solely from the `USER` or `ADMIN` role.

---

## Current Role Definitions

### USER

```text
Purpose:
Standard platform user.

Initial assignment:
Automatically assigned during public registration.

Role management:
Cannot assign or remove roles.

Role consultation:
Can consult only their own roles.
```

### ADMIN

```text
Purpose:
Authorized administrative user.

Initial assignment:
Not assigned through public registration.

Role management:
May assign and remove user-role associations.

Role consultation:
May consult roles assigned to other users.
```

---

## Conclusion

Kora currently uses `USER` and `ADMIN` as its base roles.

The Identity service controls role creation, assignment, persistence, consultation, modification, and inclusion in the signed identity context.

These role definitions establish the foundation for defining fine-grained permissions for individual operations in future authorization work.