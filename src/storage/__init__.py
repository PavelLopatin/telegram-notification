from config import settings
from .client import AsyncRedisOverride


redis_client = AsyncRedisOverride(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password,
    db=settings.redis_db,
)
