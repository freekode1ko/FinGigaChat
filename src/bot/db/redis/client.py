import redis.asyncio as redis

from configs.config import redis_host

redis_client = redis.Redis(host=redis_host, port=6379, decode_responses=True)
