import os
import redis


REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise RuntimeError("REDIS_URL is not configured.")

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)


def check_redis_connection():
    try:
        return redis_client.ping()
    except redis.RedisError:
        return False
