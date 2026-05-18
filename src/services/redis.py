"""
Redis client setup for application-level caching.
 
The client is initialized once at module load time and reused
across all requests via dependency injection.
"""
 
import redis.asyncio as redis
from src.conf.config import settings
 
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)
"""
Async Redis client instance connected to the URL defined in settings.
 
Responses are automatically decoded from bytes to strings
(``decode_responses=True``).
"""
 