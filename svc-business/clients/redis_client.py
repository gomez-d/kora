import redis

from django.conf import settings


redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


def check_redis_connection():
    try:
        return redis_client.ping()
    except redis.RedisError:
        return False
