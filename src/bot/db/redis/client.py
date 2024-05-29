"""Подключение к Redis."""

import redis.asyncio as redis

from configs.config import redis_host, redis_password, redis_port

redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password,  decode_responses=True)
