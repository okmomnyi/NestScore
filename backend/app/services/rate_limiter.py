import logging
import time
from typing import Tuple

from redis.asyncio import Redis

logger = logging.getLogger(__name__)

# Rate limit configurations: (max_requests, window_seconds)
REVIEW_LIMIT = (3, 3600)         # 3 per IP per hour
CONTACT_LIMIT = (5, 3600)        # 5 per IP per hour
SUGGESTION_LIMIT = (3, 86400)    # 3 per fingerprint per 24h
FLAG_LIMIT = (10, 86400)         # 10 per IP per 24h
ADMIN_LOGIN_LIMIT = (5, 900)     # 5 per IP per 15min
ADMIN_LOGIN_LOCKOUT = 1800       # 30 min lockout after limit


async def check_rate_limit(
    redis: Redis,
    key_prefix: str,
    identifier: str,
    max_requests: int,
    window_seconds: int,
) -> Tuple[bool, int]:
    """
    Sliding window rate limiter using Redis sorted sets.
    Returns (is_allowed, retry_after_seconds).
    retry_after_seconds is 0 if allowed.
    """
    key = f"rl:{key_prefix}:{identifier}"
    now = time.time()
    window_start = now - window_seconds

    async def do_check():
        async with redis.pipeline(transaction=True) as pipe:
            # Remove expired entries
            await pipe.zremrangebyscore(key, 0, window_start)
            # Count current requests in window
            await pipe.zcard(key)
            # Add current request
            await pipe.zadd(key, {str(now): now})
            # Set expiry
            await pipe.expire(key, window_seconds)
            results = await pipe.execute()

        current_count = results[1]

        if current_count >= max_requests:
            # Find oldest entry to calculate retry-after
            oldest = await redis.zrange(key, 0, 0, withscores=True)
            if oldest:
                oldest_time = oldest[0][1]
                retry_after = int(oldest_time + window_seconds - now) + 1
            else:
                retry_after = window_seconds
            return False, retry_after

        return True, 0

    try:
        return await do_check()
    except Exception as e:
        logger.warning(f"Redis connection failed in rate limiter: {e}. Falling back to allow.")
        return True, 0


async def check_admin_login(redis: Redis, ip_hash: str) -> Tuple[bool, int]:
    """Admin login rate limit with 30-minute lockout after 5 failed attempts."""
    lockout_key = f"rl:admin_lockout:{ip_hash}"
    try:
        lockout = await redis.get(lockout_key)
        if lockout:
            ttl = await redis.ttl(lockout_key)
            return False, max(ttl, 1)

        allowed, retry_after = await check_rate_limit(
            redis, "admin_login", ip_hash, *ADMIN_LOGIN_LIMIT
        )

        if not allowed:
            # Activate 30-minute lockout
            await redis.setex(f"rl:admin_lockout:{ip_hash}", ADMIN_LOGIN_LOCKOUT, "1")
            return False, ADMIN_LOGIN_LOCKOUT

        return allowed, retry_after
    except Exception as e:
        logger.warning(f"Redis connection failed in admin login rate limiter: {e}. Falling back to allow.")
        return True, 0


async def record_review_submission(redis: Redis, ip_hash: str) -> Tuple[bool, int]:
    return await check_rate_limit(redis, "review", ip_hash, *REVIEW_LIMIT)


async def record_contact_submission(redis: Redis, ip_hash: str) -> Tuple[bool, int]:
    return await check_rate_limit(redis, "contact", ip_hash, *CONTACT_LIMIT)


async def record_suggestion_submission(redis: Redis, fingerprint_hash: str) -> Tuple[bool, int]:
    return await check_rate_limit(redis, "suggestion", fingerprint_hash, *SUGGESTION_LIMIT)


async def record_flag_submission(redis: Redis, ip_hash: str) -> Tuple[bool, int]:
    return await check_rate_limit(redis, "flag", ip_hash, *FLAG_LIMIT)
