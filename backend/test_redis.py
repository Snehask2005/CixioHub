from app.core.redis import redis_client


redis_client.set(
    "test_key",
    "hello redis"
)

value = redis_client.get(
    "test_key"
)

print(value)