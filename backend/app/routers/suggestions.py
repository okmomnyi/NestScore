import bleach
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.plot_suggestion import PlotSuggestion
from app.redis_client import get_redis
from app.services.hashing import hash_ip
from app.services.rate_limiter import record_review_submission
from app.config import settings

router = APIRouter(prefix="/api/suggestions", tags=["Suggestions"])

SANITIZE_OPTS = {"tags": [], "attributes": {}}


class SuggestionSubmit(BaseModel):
    suggested_name: str = Field(..., min_length=3, max_length=200)
    area: str = Field(..., min_length=1, max_length=100)
    notes: str | None = Field(None, max_length=1000)
    fingerprint_hash: str = Field(..., min_length=1, max_length=128)


@router.post("", status_code=201, response_model=dict)
async def submit_suggestion(
    body: SuggestionSubmit,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Submit a suggestion for a new plot to be added to NestScore."""
    raw_ip = request.client.host if request.client else "0.0.0.0"

    # Rate limit using review submission limiter (3 per hour per IP)
    try:
        redis = await get_redis()
        ip_hash = hash_ip(raw_ip, settings.IP_HASH_SALT)
        allowed, retry_after = await record_review_submission(redis, ip_hash)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="You have submitted too many suggestions recently. Please wait before submitting again.",
                headers={"Retry-After": str(retry_after)},
            )
    except HTTPException:
        raise
    except Exception:
        pass  # Redis unavailable — skip rate limiting

    clean_name = bleach.clean(body.suggested_name, **SANITIZE_OPTS)
    clean_notes = bleach.clean(body.notes, **SANITIZE_OPTS) if body.notes else None

    suggestion = PlotSuggestion(
        suggested_name=clean_name,
        area=body.area,
        notes=clean_notes,
        fingerprint_hash=body.fingerprint_hash,
        status="pending",
    )
    db.add(suggestion)
    await db.commit()
    await db.refresh(suggestion)

    return {
        "id": str(suggestion.id),
        "status": "pending",
        "message": "Your suggestion has been received. Our moderators will review it shortly.",
    }
