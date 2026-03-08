from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from app.database import engine
from app.redis_client import get_redis

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    db_status = "connected"
    redis_status = "connected"

    # Check database
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    # Check Redis
    try:
        redis = await get_redis()
        await redis.ping()
    except Exception:
        redis_status = "error"

    return {
        "status": "ok",
        "db": db_status,
        "redis": redis_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
