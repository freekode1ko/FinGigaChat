"""Подключение к Redis."""

import redis.asyncio as redis

from configs.config import redis_host, redis_port

redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
