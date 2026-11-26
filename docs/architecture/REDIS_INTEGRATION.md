# Redis Integration

## 1. Overview

Redis is integrated into the Kora architecture as an infrastructure component responsible for enabling asynchronous communication between the Business and AI microservices.

Its integration establishes the foundation for exchanging events and AI processing requests without requiring long-running synchronous HTTP requests.

The integration is part of HU-038 (Redis Integration).

## 2. Architecture

Redis is used as an intermediary communication component between the following microservices:

- **Business Microservice:** Publishes events and AI processing requests.
- **Redis:** Stores and transports messages using Redis Streams.
- **AI Microservice:** Consumes AI processing requests and publishes processing results.

The API Gateway also communicates directly with the AI microservice through HTTP for synchronous or direct requests.

### Communication overview

```text
                 API Gateway
                      |
                      | HTTP
                      v
                AI Microservice
                      ^
                      |
                Redis Streams
                      |
                      v
              Business Microservice
```

The Redis communication channel and the direct API Gateway-to-AI connection serve different purposes and operate independently.

## 3. Technology Selection

The following technologies are used:

| Component | Technology |
|---|---|
| Message broker | Redis 7 |
| Messaging mechanism | Redis Streams |
| Python Redis client | redis-py |
| Containerization | Docker |
| Orchestration | Docker Compose |

Redis Streams was selected because it supports persistent message streams, consumer groups, message acknowledgment, and pending message management.

These capabilities provide the foundation for reliable asynchronous communication.

## 4. Redis Configuration

Redis is configured as a service in the root `docker-compose.yml` file.

### Docker Compose service

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes
  ports:
    - "${REDIS_PORT:-6379}:6379"
  volumes:
    - redis_data:/data
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 5s
    timeout: 3s
    retries: 5
  restart: unless-stopped
```

### Configuration details

- **Image:** `redis:7-alpine`.
- **Port:** Redis uses port `6379` inside the container.
- **Port mapping:** The host port is configurable through `REDIS_PORT`, defaulting to `6379`.
- **Persistence:** Append Only File (AOF) is enabled.
- **Volume:** `redis_data` stores persistent Redis data.
- **Healthcheck:** Docker periodically verifies Redis availability using `redis-cli ping`.
- **Restart policy:** `unless-stopped` allows Docker to restart the service after failures unless it was explicitly stopped.

The named volume must also be declared in the root Compose configuration:

```yaml
volumes:
  postgres_data:
  mongo_data:
  redis_data:
```

## 5. Environment Variables

Redis connection settings are configured through environment variables to support both local development and Docker execution.

The following variable is required by the Business and AI microservices:

| Variable | Local development | Docker |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | `redis://redis:6379/0` |

The local configuration uses `localhost` because the services connect to Redis through the published host port.

The Docker configuration uses `redis` as the hostname because it corresponds to the Redis service name in the Docker Compose network.

The Redis URL should be included in the corresponding environment example files:

- `svc-business/.env.example`
- `svc-business/.env.docker.example`
- `svc-ai/.env.example`
- `svc-ai/.env.docker.example`

Actual environment files containing credentials or sensitive configuration must not be committed to the repository.

## 6. Microservice Integration

### 6.1 Business Microservice

The Business microservice uses the `redis` Python package to establish a Redis connection.

The implementation is located at:

`svc-business/clients/redis_client.py`

The client obtains the connection URL from Django settings and creates a Redis client using `redis.from_url()`.

Connection availability is verified through the Redis `PING` command.

### 6.2 AI Microservice

The AI microservice also uses the `redis` Python package.

The implementation is located at:

`svc-ai/app/clients/redis_client.py`

The Redis URL is obtained from the environment variables loaded by the application.

Both clients implement a connection verification function that returns:

- `True` when Redis responds successfully.
- `False` when a Redis connection error occurs.

### 6.3 Dependencies

The Redis Python client is declared in the `requirements.txt` file of both microservices.

This ensures that Redis connectivity is available in local virtual environments and Docker images.

## 7. Connectivity Verification

The following commands can be used to verify Redis connectivity.

### 7.1 Redis availability

```powershell
docker compose exec redis redis-cli ping
```

Expected response:

```text
PONG
```

### 7.2 Business connectivity

```powershell
docker compose exec svc-business python manage.py shell -c "from clients.redis_client import check_redis_connection; print(check_redis_connection())"
```

Expected response:

```text
True
```

### 7.3 AI connectivity

```powershell
docker compose exec svc-ai python -c "from app.clients.redis_client import check_redis_connection; print(check_redis_connection())"
```

Expected response:

```text
True
```

## 8. Availability and Recovery Testing

Redis availability was tested by stopping and restarting the Redis container.

### 8.1 Redis unavailable

Stop Redis:

```powershell
docker compose stop redis
```

Execute the connectivity verification commands for both microservices.

Expected response:

```text
False
```

Both microservices should remain running while Redis is unavailable.

### 8.2 Redis recovery

Restart Redis:

```powershell
docker compose start redis
```

Verify that Redis becomes healthy:

```powershell
docker compose ps redis
```

Once Redis reports `healthy`, execute the connectivity verification commands again.

Expected response:

```text
True
```

### 8.3 Test results

| Test | Business | AI |
|---|---|---|
| Redis available | True | True |
| Redis stopped | False | False |
| Redis restarted | True | True |

These tests confirm that both microservices can detect Redis unavailability and successfully establish connections again after Redis becomes available.

They do not verify automatic reconnection during active message processing, message delivery guarantees, or consumer recovery. Those behaviors will be implemented and tested in subsequent user stories.

## 9. Messaging Architecture and Future Implementation

Redis Streams is the selected messaging mechanism for asynchronous communication.

The following streams are defined as the planned communication channels:

| Stream | Producer | Consumer |
|---|---|---|
| `ai:requests` | Business | AI |
| `ai:results` | AI | Business |

The implementation of publishing, consuming, acknowledgment, retry handling, and message recovery is covered by subsequent user stories:

- **HU-039:** Business Event Publishing.
- **HU-040:** Event Consumer Implementation.
- **HU-041:** AI Asynchronous Processing.

These functionalities are not part of the current HU-038 implementation.

## 10. Scope of HU-038

HU-038 establishes the Redis infrastructure and connection configuration required by the Kora microservices.

The completed scope includes:

- Redis integration into Docker Compose.
- Redis persistence configuration.
- Redis environment variable configuration.
- Selection of Redis Streams as the messaging mechanism.
- Redis client implementation in Business and AI.
- Local and Docker connection verification.
- Redis availability and recovery testing.

Message publishing and consumption are intentionally excluded from this user story and will be implemented in the corresponding subsequent user stories.

## 10. Message Structure and JSON Contracts

Redis Streams messages follow a standardized JSON structure to ensure consistent communication between the Business and AI microservices.

The message contract is designed to support multiple AI operations, including food recognition from images and personalized food recommendations.

### 10.1 Common Message Structure

All messages share the following structure:

```json
{
  "event_id": "unique-event-identifier",
  "event_type": "event.type",
  "timestamp": "2026-11-24T18:00:00Z",
  "data": {
    "request_id": "unique-request-identifier",
    "user_id": "user-identifier",
    "operation": "operation-name",
    "payload": {}
  }
}
```

| Field | Description |
|---|---|
| `event_id` | Unique identifier for the event. |
| `event_type` | Identifies the type of event being transmitted. |
| `timestamp` | Date and time when the event was generated, in ISO 8601 format. |
| `data` | Contains the information associated with the event. |
| `request_id` | Unique identifier for the AI processing request. Used for correlation and idempotency. |
| `user_id` | Identifies the user associated with the request. |
| `operation` | Specifies the AI operation to execute. |
| `payload` | Contains the input data or references required by the operation. |

### 10.2 AI Processing Request

Business publishes AI processing requests to the `ai:requests` stream.

The event type is:

`ai.processing.requested`

Example:

```json
{
  "event_id": "evt-001",
  "event_type": "ai.processing.requested",
  "timestamp": "2026-11-24T18:00:00Z",
  "data": {
    "request_id": "req-001",
    "user_id": "user-123",
    "operation": "food_recognition",
    "payload": {
      "image_reference": "storage://images/food-001.jpg"
    }
  }
}
```

The `image_reference` field contains a reference to the stored image. Binary image data must not be transmitted directly through Redis Streams.

For food recommendation requests, the same contract is used with a different operation and payload.

Example:

```json
{
  "event_id": "evt-002",
  "event_type": "ai.processing.requested",
  "timestamp": "2026-11-24T18:05:00Z",
  "data": {
    "request_id": "req-002",
    "user_id": "user-123",
    "operation": "food_recommendation",
    "payload": {
      "nutrition_profile": {},
      "preferences": [],
      "allergies": [],
      "health_conditions": [],
      "calorie_goal": 2000
    }
  }
}
```

The payload must contain only the information required by the requested operation. Whenever possible, references should be used instead of duplicating sensitive user information.

### 10.3 Successful Processing Result

After successfully processing a request, AI publishes a result to the `ai:results` stream.

The event type is:

`ai.processing.completed`

Example:

```json
{
  "event_id": "evt-003",
  "event_type": "ai.processing.completed",
  "timestamp": "2026-11-24T18:01:30Z",
  "data": {
    "request_id": "req-001",
    "user_id": "user-123",
    "operation": "food_recognition",
    "status": "completed",
    "result": {
      "food_items": [],
      "confidence": 0.95
    }
  }
}
```

The `result` field contains the output generated by the AI operation. Its internal structure depends on the operation being executed.

### 10.4 Failed Processing Result

If an AI operation cannot be completed due to a functional or permanent processing error, AI publishes a failure result to the `ai:results` stream.

The event type is:

`ai.processing.failed`

Example:

```json
{
  "event_id": "evt-004",
  "event_type": "ai.processing.failed",
  "timestamp": "2026-11-24T18:02:00Z",
  "data": {
    "request_id": "req-001",
    "user_id": "user-123",
    "operation": "food_recognition",
    "status": "failed",
    "error": {
      "code": "AI_PROCESSING_ERROR",
      "message": "The requested operation could not be completed."
    }
  }
}
```

Error messages must not expose credentials, secrets, internal stack traces, or other sensitive implementation details.

### 10.5 Event Types

| Event type | Producer | Stream | Purpose |
|---|---|---|---|
| `ai.processing.requested` | Business | `ai:requests` | Requests AI processing. |
| `ai.processing.completed` | AI | `ai:results` | Reports successful processing. |
| `ai.processing.failed` | AI | `ai:results` | Reports processing failure. |

### 10.6 Message Processing Considerations

The following rules guide the future implementation of Redis Streams consumers and producers:

- Each event must have a unique `event_id`.
- Each AI request must have a unique `request_id`.
- The `request_id` must be preserved in the corresponding result to correlate requests and responses.
- Consumers must support idempotent processing to prevent duplicate execution when messages are delivered more than once.
- Messages must be acknowledged only after successful processing and, for AI failures, after the failure result has been successfully published.
- Consumer Groups will be used to coordinate message processing.
- Pending messages must be recoverable if a consumer becomes unavailable.
- Infrastructure errors and functional processing errors must be handled separately.

The implementation of these mechanisms belongs to HU-039, HU-040, and HU-041.
