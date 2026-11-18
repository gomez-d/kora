# Kora API Gateway — Rate Limiting and Abuse Protection

## 1. Overview

The API Gateway is the single entry point for frontend requests to the Kora backend services.

It is responsible for applying rate limiting policies to sensitive and authenticated endpoints to reduce excessive requests and protect backend services against application-level abuse.

Rate limiting is implemented using Django REST Framework (DRF) throttling mechanisms.

The Gateway applies different request limits depending on the endpoint and the identity used to track requests.

## 2. Purpose and Scope

This document describes the rate limiting policies implemented in the Kora API Gateway.

It covers:

- Identification of sensitive endpoints.
- Rate limiting policies by IP address and authenticated user.
- Throttling implementation using Django REST Framework.
- HTTP 429 responses when request limits are exceeded.
- Verification through automated tests.
- Security considerations and implementation limitations.

The implementation applies at the API Gateway level. Frontend requests are subject to these policies before being forwarded to the corresponding microservices.

## 3. Rate Limiting Policies

The API Gateway defines four rate limiting policies.

| Operation | Request Limit | Identification Method |
|---|---|---|
| User Login | 5 requests per minute | Client IP address |
| User Registration | 3 requests per hour | Client IP address |
| Token Refresh | 10 requests per minute | Client IP address |
| Authenticated Endpoints | 60 requests per minute | Authenticated User ID |

Each policy has an independent throttling scope.

The limits are configured through the `DEFAULT_THROTTLE_RATES` setting in the API Gateway Django configuration.

### 3.1 User Login

**Endpoint:**

`POST /api/identity/users/login/`

**Limit:** 5 requests per minute per IP address.

This policy limits repeated authentication attempts from the same IP address.

### 3.2 User Registration

**Endpoint:**

`POST /api/identity/users/register/`

**Limit:** 3 requests per hour per IP address.

This policy restricts excessive account creation attempts from the same IP address.

### 3.3 Token Refresh

**Endpoint:**

`POST /api/identity/users/token/refresh/`

**Limit:** 10 requests per minute per IP address.

This policy limits repeated refresh token requests.

### 3.4 Authenticated Endpoints

**Limit:** 60 requests per minute per authenticated user.

This policy applies to authenticated requests forwarded through the Business and AI proxies, as well as other Identity endpoints that do not have a dedicated public throttling policy.

Requests are identified using the authenticated user's `user_id` obtained from the JWT authentication process.

The same throttling scope is used across the Business and AI proxies. Therefore, requests to both services share the same authenticated-user limit.

## 4. Protected Endpoints

The following table summarizes the endpoints and proxy components covered by the implemented policies.

| Component | Endpoint or Scope | Rate Limit |
|---|---|---|
| Identity Proxy | `/api/identity/users/login/` | 5/minute per IP |
| Identity Proxy | `/api/identity/users/register/` | 3/hour per IP |
| Identity Proxy | `/api/identity/users/token/refresh/` | 10/minute per IP |
| Identity Proxy | Other authenticated Identity endpoints | 60/minute per user |
| Business Proxy | `/api/business/{path}/` | 60/minute per user |
| AI Proxy | `/api/ai/{path}/` | 60/minute per user |

The limits are enforced by the API Gateway before forwarding requests to the corresponding microservices.

Health check endpoints are not assigned a dedicated throttling policy under this implementation.

## 5. Identification Mechanisms

The API Gateway uses two identification mechanisms depending on the endpoint being accessed.

### 5.1 IP-Based Identification

Login, registration, and token refresh requests are identified using the client's IP address.

The implementation obtains the address from:

`request.META["REMOTE_ADDR"]`

This value is used to generate the throttling cache key.

The implementation does not use the `X-Forwarded-For` header as the client identifier.

This avoids relying on a client-supplied forwarding header that could be manipulated when the Gateway is directly exposed.

If a trusted reverse proxy is introduced in a future deployment, the client IP identification strategy must be reviewed and configured according to that network topology.

### 5.2 Authenticated User Identification

Authenticated requests are identified using:

`request.user.id`

The API Gateway obtains the authenticated user identity through its JWT authentication mechanism.

The resulting user ID is used to generate the throttling cache key.

Requests from the same authenticated user share the same rate limit, regardless of whether they access the Business or AI proxy.

Unauthenticated requests are not assigned an authenticated-user throttling key.

## 6. HTTP 429 — Too Many Requests

When a client exceeds the configured request limit, the API Gateway returns:

`HTTP 429 Too Many Requests`

The request is rejected before being forwarded to the corresponding microservice.

This response indicates that the client has exceeded the allowed request rate for the applicable throttling policy.

The client must wait until requests are permitted again before retrying.

The response is generated by Django REST Framework's throttling exception handling mechanism.

## 7. Implementation Details

### 7.1 Throttling Classes

The implementation is located in:

`api-gateway/gateway/throttling.py`

The following custom throttling classes are implemented:

| Class | Responsibility |
|---|---|
| `IPRateThrottle` | Base class for IP-based request identification |
| `LoginRateThrottle` | Applies the login request limit |
| `RegistrationRateThrottle` | Applies the registration request limit |
| `RefreshRateThrottle` | Applies the token refresh request limit |
| `AuthenticatedUserRateThrottle` | Applies the authenticated-user request limit |

The custom classes extend Django REST Framework's `SimpleRateThrottle`.

### 7.2 Rate Configuration

The request rates are defined in the API Gateway's `REST_FRAMEWORK` configuration.

| Scope | Configured Rate |
|---|---|
| `login` | `5/min` |
| `registration` | `3/hour` |
| `refresh` | `10/min` |
| `authenticated_user` | `60/min` |

### 7.3 View Integration

The throttling classes are selected through the `get_throttles()` method in the corresponding API Gateway views.

- `IdentityProxyView` selects the appropriate policy according to the requested Identity endpoint.
- `BusinessProxyView` applies authenticated-user throttling.
- `AIProxyView` applies authenticated-user throttling.

The custom `dispatch()` implementations execute the DRF initialization process before forwarding requests.

This ensures that permission checks and throttling are performed before requests reach the target microservices.

## 8. Verification and Tests

The throttling implementation is verified through automated tests located in:

`api-gateway/gateway/tests/test_throttling.py`

The tests verify that requests exceeding the configured limits receive HTTP 429 responses.

### 8.1 Test Coverage

| Test | Expected Behavior |
|---|---|
| Login throttling | The sixth request within the configured limit window receives HTTP 429 |
| Registration throttling | The fourth request within the configured limit window receives HTTP 429 |
| Refresh throttling | The eleventh request within the configured limit window receives HTTP 429 |
| Business throttling | The sixty-first authenticated request within the configured limit window receives HTTP 429 |
| AI throttling | The sixty-first authenticated request within the configured limit window receives HTTP 429 |

The tests also verify that requests within the configured limits reach the proxy forwarding operation.

External service requests are mocked during testing to avoid depending on the availability of other microservices.

### 8.2 Verification Results

The throttling test suite was executed inside the API Gateway Docker container.

Execution command:

```bash
python manage.py test gateway.tests.test_throttling
```

Verification result:

- Total tests: 5.
- Passed tests: 5.
- Failed tests: 0.

All implemented throttling policies returned the expected HTTP 429 response when their configured limits were exceeded.

**Result:** The API Gateway rate limiting implementation was successfully verified in the local Docker Compose environment.

## 9. Security Considerations

The following considerations apply to the current implementation:

- Rate limiting is enforced centrally by the API Gateway.
- Sensitive authentication-related endpoints use IP-based identification.
- Authenticated requests use JWT-derived user identification.
- Requests exceeding configured limits are rejected before reaching the target microservices.
- The implementation does not trust client-supplied `X-Forwarded-For` values for IP identification.
- Rate limiting is an application-level abuse protection mechanism and does not replace network-level DDoS protection.

### 9.1 Cache Considerations

Django REST Framework throttling uses Django's cache framework to maintain request counters.

The current API Gateway configuration uses Django's default local-memory cache because no shared cache backend is configured.

This configuration is suitable for the current local Docker Compose execution environment, which runs a single API Gateway container.

However, local-memory cache counters are not shared across multiple Gateway processes or instances.

A future deployment involving multiple workers or Gateway replicas should use a shared cache backend, such as Redis, to maintain consistent throttling counters across instances.

Additionally, Django REST Framework throttling is not guaranteed to provide strictly atomic request counting under concurrent requests.

These limitations must be considered when adapting the implementation for production workloads.

## 10. Future Improvements

The following improvements may be considered for future deployments:

- Integration with a shared Redis cache backend for distributed throttling.
- Configuration of trusted reverse proxy IP forwarding when applicable.
- Additional monitoring of rate limit violations.
- Review and adjustment of request limits according to production traffic patterns.
- Additional automated tests for IP and user identification isolation.

Any future improvements must preserve the API Gateway's responsibility as the centralized entry point for backend requests and maintain the existing microservice architecture.