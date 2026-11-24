# HU-033 - Authenticated Session Management

## 1. Objective

Manage authenticated user sessions in the Kora frontend,
including authentication state, token renewal and logout.

## 2. Session Storage

The frontend uses sessionStorage to store:

- kora_user
- kora_access_token
- kora_refresh_token

Session data remains available during navigation and page
reloads within the browser tab.

## 3. Authentication State

The kora-session.js module centralizes:

- Authentication state.
- User information.
- Protected route validation.
- Logout operations.

## 4. Access Token

The kora-api.js module automatically attaches:

Authorization: Bearer <access_token>

to protected API requests.

## 5. Token Renewal

When the access token expires or the API Gateway rejects it,
the frontend sends the refresh token to:

POST /api/identity/users/token/refresh/

The frontend stores the new access and refresh tokens.

Refresh requests are synchronized to prevent concurrent
renewal operations.

## 6. Protected Routes

Private frontend pages require a valid authenticated session.

Unauthenticated users are redirected to login.html.

## 7. Logout

The frontend sends the refresh token to:

POST /api/identity/users/logout/

Identity revokes the refresh token using the blacklist.

The frontend clears local session information.

## 8. Invalid Sessions

When the refresh token is invalid, expired or revoked,
the frontend clears authentication data and redirects
the user to login.

Network failures are handled separately from invalid credentials.

## 9. Security Considerations

- Tokens are stored in sessionStorage.
- Access tokens are sent using the Bearer scheme.
- Refresh tokens are rotated by Identity.
- Backend authorization remains mandatory.
- Frontend route protection does not replace backend security.