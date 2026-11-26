# HU-025 — JWT Issuance

## 1. Objective

Implement JWT token issuance in the `svc-identity` microservice, allowing users to authenticate using valid credentials and generate access and refresh tokens.

## 2. Implementation

The `djangorestframework-simplejwt` library was used to manage JWT token generation and validation.

Token expiration times were configured in `config/settings.py`.

- Access token: 15 minutes.
- Refresh token: 1 day.

Token generation was integrated into the existing login endpoint, avoiding the creation of a second login endpoint.

## 3. Implemented Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| POST | `/api/users/login/` | Authenticates the user and generates JWT tokens. |
| POST | `/api/users/token/refresh/` | Renews the access token using a valid refresh token. |

## 4. Login and Token Issuance

**Request:**
```json
{
    "username": "test_user",
    "password": "test_password"
}
```

**Expected Response:**
```json
{
    "success": true,
    "message": "Login successful.",
    "data": {
        "user_id": "USER-UUID",
        "access": "ACCESS_TOKEN",
        "refresh": "REFRESH_TOKEN"
    }
}
```

The user identifier is returned as a UUID. The tokens allow the authenticated user to be identified and access to protected resources to be managed.

## 5. Access Token Renewal

**Request:**
```json
{
    "refresh": "REFRESH_TOKEN"
}
```

**Expected Response:**
```json
{
    "access": "NEW_ACCESS_TOKEN"
}
```

## 6. Using the Access Token

To access endpoints that require authentication, the token must be sent in the HTTP header:

```http
Authorization: Bearer ACCESS_TOKEN
```

## 7. Tests Performed

Manual tests were performed using Insomnia while the microservice was running through Docker Compose.

| Test | Expected Result | Result |
| ---------------------------------- | --------------------------------- | --------- |
| User registration | User is registered successfully. | Passed |
| Login with valid credentials | Returns access and refresh tokens. | Passed |
| Login with invalid credentials | Rejects authentication. | Passed |
| Renewal with a valid refresh token | Returns a new access token. | Passed |
| Use of a tampered token | Rejects the token. | Passed |
| Use of an expired token | Rejects the token. | Passed |

## 8. Running with Docker

To rebuild the Identity container:

```bash
docker compose up -d --build svc-identity
```

To view the logs:

```bash
docker compose logs -f svc-identity
```

## 9. OpenAPI Documentation

The OpenAPI definitions were updated to include the login and token renewal endpoints.

The API schema documentation is available at:

`http://localhost:8001/api/schema/`

## 10. Result

JWT issuance was successfully implemented within the Identity microservice login flow. The generation of access and refresh tokens, token renewal, and rejection of invalid credentials and tokens were verified.

**User Story:** HU-025 — JWT Issuance.

**Status:** Implementation and testing completed.