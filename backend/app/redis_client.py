import redis.asyncio as redis_asyncio
from app.config import settings

redis_pool: redis_asyncio.Redis | None = None


async def get_redis() -> redis_asyncio.Redis:
    global redis_pool
    if redis_pool is None:
        redis_pool = redis_asyncio.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_pool


async def close_redis():
    global redis_pool
    if redis_pool:
        await redis_pool.aclose()
        redis_pool = None
