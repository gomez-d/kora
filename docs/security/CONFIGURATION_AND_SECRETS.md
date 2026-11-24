# Configuration and Secrets Management

## 1. Purpose and Scope

This document describes how configuration variables and sensitive information are managed across the Kora microservices architecture.

Its purpose is to ensure that application configuration and credentials are externalized from source code, allowing each service to operate with environment-specific settings without exposing sensitive information.

It covers:

- Environment variable management.
- Local development configuration.
- Docker Compose configuration.
- Docker Secrets for sensitive credentials.
- Preparation for future integration with Google Cloud Secret Manager.

The implementation described here corresponds to Kora V2. Future production deployments may introduce additional secret management mechanisms without requiring credentials to be embedded in application code or version-controlled configuration files.

## 2. Environment Variables Management

Kora uses environment variables to configure application behavior and service connections.

Each microservice manages its own configuration independently. This allows services to use different settings depending on the execution environment.

The following principles apply:

- Configuration values must not be hardcoded in application source code.
- Sensitive credentials must not be stored in version-controlled files.
- Each service must access only the configuration required for its operation.
- Environment-specific values must be maintained separately.
- Example environment files must contain placeholders or non-sensitive values only.

### 2.1 Configuration Files

Each microservice uses the following configuration files where applicable:

| File | Purpose |
|---|---|
| `.env` | Local development configuration. |
| `.env.example` | Documents the required local environment variables without exposing credentials. |
| `.env.docker` | Contains configuration values specific to Docker execution. |
| `.env.docker.example` | Documents Docker-specific variables without exposing credentials. |

The `.env` and `.env.docker` files are complementary.

Docker Compose loads the service's `.env` file first and `.env.docker` afterward. Therefore, Docker-specific values override local values when both define the same variable.

The `.env.example` and `.env.docker.example` files serve as configuration references and must not contain real credentials.

Docker Compose uses the `env_file` directive to inject service-specific environment variables into containers. The files are loaded in the declared order, and subsequent files override previously defined values.

These files are read from the host and do not need to be included in Docker images. The root `.env` file is handled separately for Compose variable interpolation.

## 3. Service Configuration

Each Kora service maintains its own configuration.

The following table identifies the main configuration variables used by each component.

### 3.1 API Gateway

| Variable | Purpose |
|---|---|
| `ENVIRONMENT` | Identifies the execution environment. |
| `PORT` | Defines the application port. |
| `DEBUG` | Enables or disables debug mode. |
| `SECRET_KEY` | Django application secret key. |
| `ALLOWED_HOSTS` | Defines the permitted hostnames. |
| `IDENTITY_SERVICE_URL` | Internal URL of the Identity service. |
| `BUSINESS_SERVICE_URL` | Internal URL of the Business service. |

### 3.2 Identity Service

| Variable | Purpose |
|---|---|
| `ENVIRONMENT` | Identifies the execution environment. |
| `PORT` | Defines the application port. |
| `DEBUG` | Enables or disables debug mode. |
| `SECRET_KEY` | Django application secret key. |
| `ALLOWED_HOSTS` | Defines the permitted hostnames. |
| `DB_HOST` | PostgreSQL database host. |
| `DB_PORT` | PostgreSQL database port. |
| `DB_NAME` | Identity database name. |
| `DB_USER` | Identity database user. |
| `DB_PASSWORD` | Database password for local development. |
| `DB_PASSWORD_FILE` | Optional path to an externally supplied database password file. |
| `UNSTRUCTURED_DATA_SERVICE_URL` | Internal URL of the Unstructured Data service. |
| `UNSTRUCTURED_DATA_SERVICE_TOKEN` | Authentication token for internal security audit requests. |
| `FRONTEND_PASSWORD_RESET_URL` | Frontend URL used to generate password recovery links. |

### 3.3 Business Service

| Variable | Purpose |
|---|---|
| `ENVIRONMENT` | Identifies the execution environment. |
| `PORT` | Defines the application port. |
| `DEBUG` | Enables or disables debug mode. |
| `SECRET_KEY` | Django application secret key. |
| `ALLOWED_HOSTS` | Defines the permitted hostnames. |
| `DB_HOST` | PostgreSQL database host. |
| `DB_PORT` | PostgreSQL database port. |
| `DB_NAME` | Business database name. |
| `DB_USER` | Business database user. |
| `DB_PASSWORD` | Database password for local development. |
| `DB_PASSWORD_FILE` | Optional path to an externally supplied database password file. |
| `IDENTITY_SERVICE_URL` | Internal URL of the Identity service. |
| `UNSTRUCTURED_DATA_SERVICE_URL` | Internal URL of the Unstructured Data service. |

### 3.4 Unstructured Data Service

| Variable | Purpose |
|---|---|
| `ENVIRONMENT` | Identifies the execution environment. |
| `PORT` | Defines the application port. |
| `DEBUG` | Enables or disables debug mode. |
| `SECRET_KEY` | Django application secret key. |
| `ALLOWED_HOSTS` | Defines the permitted hostnames. |
| `MONGODB_URL` | MongoDB connection URI. |

### 3.5 AI Service

| Variable | Purpose |
|---|---|
| `ENVIRONMENT` | Identifies the execution environment. |
| `PORT` | Defines the application port. |
| `GROQ_API_KEY` | Authentication key for the external Groq AI provider. |
| `CORS_ALLOWED_ORIGINS` | Defines the permitted CORS origins. |

### 3.6 Frontend

The frontend is built and served through its Docker configuration.

The following root environment variable is used to configure its external port in Docker Compose:

| Variable | Purpose |
|---|---|
| `FRONTEND_PORT` | Defines the host port used to access the frontend. |

The frontend does not receive direct database credentials or access to internal microservice configuration secrets.

### 3.7 Shared Docker Compose Configuration

The root `.env` file defines shared configuration variables used by Docker Compose for environment interpolation.

| Variable | Purpose |
|---|---|
| `POSTGRES_PORT` | Defines the host port exposed by PostgreSQL. |
| `MONGO_PORT` | Defines the host port exposed by MongoDB. |
| `POSTGRES_USER` | Defines the PostgreSQL administrative user. |
| `POSTGRES_DB` | Defines the PostgreSQL initialization database. |
| `GATEWAY_PORT` | Defines the host port exposed by the API Gateway. |
| `IDENTITY_PORT` | Defines the host port exposed by the Identity service. |
| `BUSINESS_PORT` | Defines the host port exposed by the Business service. |
| `UNSTRUCTURED_DATA_PORT` | Defines the host port exposed by the Unstructured Data service. |
| `AI_PORT` | Defines the host port exposed by the AI service. |
| `FRONTEND_PORT` | Defines the host port exposed by the frontend. |

Database passwords are provided through Docker Secrets rather than root environment variables.

These variables configure host-to-container port mappings and shared infrastructure settings. They do not automatically become environment variables inside every container.


### 3.8 Password Recovery Configuration (HU-070)

The password recovery workflow requires additional configuration in the Identity Service and API Gateway.

#### Identity Service

| Configuration | Purpose |
|---|---|
| `FRONTEND_PASSWORD_RESET_URL` | Defines the frontend password reset URL included in recovery instructions. |
| `UNSTRUCTURED_DATA_SERVICE_URL` | Defines the internal destination for security audit events. |
| `UNSTRUCTURED_DATA_SERVICE_TOKEN` | Authenticates communication with the audit service. |
| `MAILERS` | Configures Django's email delivery backend. |
| `REST_FRAMEWORK.DEFAULT_THROTTLE_RATES` | Configures password recovery request limits. |
| `CACHES` | Configures storage for rate-limiting counters. |

In the tested local development environment, the Identity Service uses Django's console email backend:

```python
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    }
}
```

This backend displays recovery instructions in the Identity Service console instead of sending messages through an external email provider.

The local configuration uses a PostgreSQL-backed Django database cache for Identity Service throttling.

#### API Gateway

The API Gateway defines the following password recovery throttling scopes:

| Scope | Rate |
|---|---|
| `password_reset_request` | `5/hour` per client IP |
| `password_reset_confirm` | `10/hour` per client IP |

The Gateway identifies clients using `REMOTE_ADDR` and applies these limits before forwarding requests to the Identity Service.

The Identity Service enforces its own additional request limits independently of the Gateway.

#### Security Considerations

- Recovery tokens and passwords must not be stored in environment files or application logs.
- Internal audit authentication tokens must remain outside version control.
- Production email delivery requires an appropriately configured email provider.
- The configured frontend recovery URL must match the deployed frontend address.
- Trusted proxy configuration must be reviewed before production deployment.
- Rate-limiting caches should use shared storage when multiple application instances are deployed.

For implementation details and test results, see [HU-070 — Password Recovery](../user-stories/HU-070.md).

## 4. Local Development Configuration

For local development, each microservice uses its own `.env` file.

The root `.env` file is used by Docker Compose for variable interpolation and does not automatically configure services running independently outside Docker.

These files contain the configuration required to run services independently on the development machine.

The root `.env` file contains shared Docker Compose configuration, including exposed ports and PostgreSQL initialization settings.

### 4.1 Configuration Procedure

1. Create the required `.env` files using the corresponding `.env.example` files as references.
2. Provide the necessary local configuration values.
3. Configure database connection parameters according to the local development environment.
4. Provide the required application credentials through local environment files.
5. Ensure that real `.env` files are excluded from version control.

### 4.2 Local Database Configuration

For local development:

- Identity connects to its own PostgreSQL database.
- Business connects to its own PostgreSQL database.
- Unstructured Data connects to MongoDB.
- The AI service receives its external provider credentials through environment variables.

Identity and Business use independent PostgreSQL users and passwords.

Each application must use only its corresponding database credentials.

## 5. Docker Compose Configuration

Docker Compose provides the configuration required to execute the Kora services in containers.

Each service declares its environment files through the `env_file` configuration.

The root `.env` file is used by Docker Compose for variable interpolation, such as exposed ports and PostgreSQL initialization settings. It is not automatically injected into every container.

### 5.1 Environment File Loading

Each service loads its local `.env` file followed by its `.env.docker` file.

The second file overrides variables defined in the first one when necessary.

This approach allows Docker-specific values to replace local settings, including:

- Database hostnames.
- Internal service URLs.
- Application ports.
- Host configuration.

Variables that remain identical between environments do not need to be duplicated in `.env.docker`.

### 5.2 Internal Service Communication

Within Docker Compose, services communicate using their respective service names and internal container ports.

The internal URLs are configured through environment variables.

For example:

- `http://svc-identity:8000`
- `http://svc-business:8000`
- `http://svc-unstructured-data:8000`

The frontend communicates with the API Gateway, which remains the only public API entry point.

Internal services are not accessed directly by the frontend.

## 6. Docker Secrets

Docker Secrets are used to provide sensitive database credentials to the PostgreSQL container and the services that require them.

This prevents database passwords from being stored directly in Docker Compose configuration or exposed as container environment variable values.

### 6.1 Defined Secrets

The following secrets are configured:

| Secret | Purpose |
|---|---|
| `postgres_password` | PostgreSQL initialization and administrative password. |
| `identity_password` | Identity database user password. |
| `business_password` | Business database user password. |

Each secret is provided through an independent file located in:

`docker/postgres/secrets/`

These files are excluded from version control.

### 6.2 Secret Mounting

Docker Compose mounts secrets into containers under:

`/run/secrets/`

The PostgreSQL container receives all three secrets:

- `postgres_password`
- `identity_password`
- `business_password`

The Identity service receives only `identity_password`.

The Business service receives only `business_password`.

This restricts access to sensitive credentials according to each component's responsibilities.

### 6.3 Application Secret Reading

Identity and Business read their database passwords from the corresponding secret files.

The application configuration supports an optional `DB_PASSWORD_FILE` variable to specify an alternative external secret file path.

If the configured file exists, the application reads the password from that file.

If the file does not exist, the application falls back to the `DB_PASSWORD` environment variable, which supports local development.

The database configuration is validated during application startup. Missing required database configuration causes the application to raise a configuration error.

### 6.4 Database Access Isolation

PostgreSQL uses independent database users for Identity and Business.

- `identity_user` owns and accesses `kora_identity`.
- `business_user` owns and accesses `kora_business`.
- The administrative PostgreSQL user is reserved for initialization and database administration.

Cross-database connection privileges are revoked to prevent application users from accessing databases belonging to other services.

This follows the principle of least privilege.

## 7. Preparation for Google Cloud Secret Manager

Kora is prepared to support a future integration with Google Cloud Secret Manager.

This integration is intended to provide centralized secret storage and controlled access to sensitive credentials in a production environment.

### 7.1 Current Implementation

In Kora V2:

- Docker Secrets provide database credentials to containers.
- Local development uses environment files.
- Application code supports reading database passwords from externally supplied files.
- Sensitive credentials are not required to be embedded in source code or version-controlled configuration files.

Google Cloud Secret Manager is not currently deployed or integrated.

### 7.2 Future Integration

A future production deployment may use Google Cloud Secret Manager to manage sensitive values such as:

- Django secret keys.
- PostgreSQL credentials.
- External AI provider API keys.
- Other service authentication credentials.

The integration may use an appropriate secret delivery mechanism to provide secret values to the application, such as mounting secrets as files or retrieving them through an authorized secret provider.

The selected mechanism must ensure that:

- Applications authenticate using appropriate Google Cloud identities.
- Access is restricted according to the principle of least privilege.
- Secrets are not exposed in source code, logs, or error messages.
- Secret rotation can be performed without embedding new credentials in application code.

The current `DB_PASSWORD_FILE` mechanism provides a file-based configuration point for future external secret delivery. Direct retrieval from Google Cloud Secret Manager would require an additional integration mechanism and is not implemented in this version.

## 8. Security Considerations

The following practices must be maintained:

- Never commit real `.env` files or secret files to the repository.
- Never include real credentials in example configuration files.
- Never hardcode passwords, API keys, or application secret keys in source code.
- Do not expose credentials in application logs or error messages.
- Do not include sensitive values in Docker image layers or Dockerfiles.
- Restrict database access to the appropriate service-specific users.
- Use independent credentials for each service.
- Keep local, Docker, and production credentials separate.
- Rotate credentials when exposure is suspected or when required by the deployment security policy.
- Grant access to sensitive configuration only to authorized components.

Docker Compose file-backed secrets provide a mechanism for mounting sensitive files into containers. They do not, by themselves, provide the centralized secret lifecycle management or production-grade secret storage offered by a dedicated secret management service.

## 9. Configuration and Execution Procedure

### 9.1 Local Development

1. Create the required `.env` files from the corresponding example files.
2. Configure each service's environment variables.
3. Configure local database connection parameters.
4. Provide the required credentials through local environment files.
5. Start the required services using their local development procedures.

### 9.2 Docker Environment

1. Create the root `.env` file using `.env.example` as a reference.
2. Create the service-specific `.env` files.
3. Create the corresponding `.env.docker` files using their example files.
4. Create the required Docker Secret files under `docker/postgres/secrets/`.
5. Verify that all required secret files exist and contain their corresponding credentials before starting Docker Compose.
6. Start the environment using Docker Compose.
7. Verify that all containers start successfully.
8. Verify that database migrations complete successfully.
9. Verify that Identity and Business connect only to their respective databases.
10. Review service logs to ensure that no sensitive information is exposed.

### 9.3 Verification

The configuration must be considered valid when:

- All required services start successfully.
- Each service receives its expected environment configuration.
- Database passwords are read from the appropriate secret files in Docker.
- Database credentials are not exposed through container environment variables.
- Identity and Business can access their respective databases.
- Cross-database access is denied.
- No real credentials are present in version-controlled configuration files.

## 10. Future Improvements

The following improvements may be introduced in future versions:

- Integration with Google Cloud Secret Manager.
- Centralized secret rotation.
- Environment-specific access policies.
- Automated secret provisioning during deployment.
- Additional monitoring and auditing of secret access.

These improvements must preserve the existing microservice separation and ensure that sensitive credentials remain external to application source code.

## 11. Verification Results

The secure configuration management implementation was verified in the local Docker Compose environment.

### 11.1 Environment Configuration

- Confirmed that each microservice uses its corresponding environment configuration.
- Verified that local environment files are excluded from version control.
- Confirmed that example environment files contain configuration placeholders rather than actual credentials.
- Verified that Docker Compose correctly injects the required configuration into the containers.

### 11.2 Docker Secrets

- Confirmed that PostgreSQL credentials are stored in separate secret files.
- Verified that PostgreSQL receives its administrative password through Docker Secrets.
- Verified that Identity and Business receive their respective database passwords through mounted secret files.
- Confirmed that database passwords are not exposed through the `DB_PASSWORD` environment variable in the application containers.

### 11.3 Database Access Isolation

- Confirmed that the Identity service can access its own database.
- Confirmed that the Business service can access its own database.
- Verified that Identity cannot connect to the Business database.
- Verified that Business cannot connect to the Identity database.
- Confirmed that each application database has its corresponding dedicated database user.

### 11.4 Container Execution

- Verified that the Docker Compose services start successfully.
- Confirmed PostgreSQL and MongoDB health checks.
- Verified successful database migrations for Identity and Business.
- Confirmed that the application services initialize without configuration errors related to the implemented secret management mechanism.

### 11.5 Version Control Security

- Verified that local `.env` files are excluded through `.gitignore`.
- Confirmed that the `docker/postgres/secrets/` directory is excluded from version control.
- Checked tracked files and found no actual environment files or secret files registered in Git.
- Confirmed that example configuration files remain available for repository documentation and setup.

### 11.6 Verification Outcome

The secure configuration management implementation was verified in the local Docker Compose environment.

The verification confirmed that:

- Application configuration is externalized from source code.
- Sensitive database credentials are supplied through Docker Secrets.
- Identity and Business use independent database credentials and access permissions.
- Local environment files and secret files are excluded from version control.
- The services start successfully with the implemented configuration.

Google Cloud Secret Manager integration has not been implemented in this version. Its future adoption is documented as a planned improvement.

**Result:** HU-035 secure configuration management requirements have been implemented and verified in the local development environment.