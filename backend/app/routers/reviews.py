import uuid
from datetime import datetime, timezone, timedelta

import bleach
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.flag import Flag
from app.models.plot import Plot
from app.models.review import Review
from app.redis_client import get_redis
from app.schemas.review import FlagSubmit, ReviewSubmit, ReviewSubmitResponse
from app.services import profanity, turnstile
from app.services.fingerprint import check_duplicate_review
from app.services.hashing import hash_fingerprint, hash_ip, hash_subnet_prefix
from app.services.rate_limiter import record_flag_submission, record_review_submission
from app.services.scoring import recalculate_plot_score
from app.services.random_username import generate_random_username
from app.config import settings

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

SANITIZE_OPTS = {"tags": [], "attributes": {}}


@router.post("", response_model=ReviewSubmitResponse, status_code=201)
async def submit_review(
    body: ReviewSubmit,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    raw_ip = request.client.host if request.client else "0.0.0.0"
    redis = await get_redis()

    # 1. Validate Turnstile token
    valid = await turnstile.verify_turnstile_token(body.turnstile_token, raw_ip)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid CAPTCHA token. Please try again.")

    # 2. Verify plot exists and is active
    plot_result = await db.execute(
        select(Plot).where(Plot.id == body.plot_id, Plot.status.in_(["active", "under_review"]))
    )
    if not plot_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Plot not found or not available for review.")

    # 3. Rate limit — 3 per IP per hour
    ip_hash = hash_ip(raw_ip, settings.IP_HASH_SALT)
    allowed, retry_after = await record_review_submission(redis, ip_hash)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="You have submitted too many reviews recently. Please wait before submitting again.",
            headers={"Retry-After": str(retry_after)},
        )

    # 4. Server-side fingerprint double-hash
    server_fp_hash = hash_fingerprint(body.fingerprint_hash, settings.FINGERPRINT_SALT)

    # 5. Check fingerprint/plot uniqueness (one review per device per plot, lifetime)
    if await check_duplicate_review(server_fp_hash, body.plot_id, db):
        raise HTTPException(status_code=409, detail="You have already reviewed this plot.")

    # 6. Profanity check — synchronous, before any DB write
    clean_text = bleach.clean(body.comment_text, **SANITIZE_OPTS)
    if profanity.is_profane(clean_text):
        raise HTTPException(status_code=400, detail=profanity.REJECTION_MESSAGE)

    # 7. Calculate subnet prefix hash
    subnet_hash = hash_subnet_prefix(raw_ip, settings.IP_HASH_SALT)

    # 8. Write review with status=active automatically (instant publish)
    publish_at = datetime.now(timezone.utc)
    review = Review(
        plot_id=body.plot_id,
        stars=body.stars,
        comment_text=clean_text,
        fingerprint_hash=server_fp_hash,
        ip_hash=ip_hash,
        subnet_prefix_hash=subnet_hash,
        nickname=body.nickname or generate_random_username(),
        status="active",
        publish_at=publish_at,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)

    # 9. Trigger score recalculation & anomaly check in background immediately
    background_tasks.add_task(
        _recalculate_after_flag, review.plot_id
    )
    from app.services.anomaly import run_anomaly_detection
    background_tasks.add_task(
        _run_anomaly, review.plot_id
    )

    return ReviewSubmitResponse(id=review.id, publish_at=review.publish_at)


async def _run_anomaly(plot_id: uuid.UUID):
    from app.database import AsyncSessionLocal
    from app.services.anomaly import run_anomaly_detection
    async with AsyncSessionLocal() as db:
        await run_anomaly_detection(plot_id, db)


@router.post("/{review_id}/flag", status_code=201)
async def flag_review(
    review_id: uuid.UUID,
    body: FlagSubmit,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    raw_ip = request.client.host if request.client else "0.0.0.0"
    redis = await get_redis()

    # Rate limit flags
    ip_hash = hash_ip(raw_ip, settings.IP_HASH_SALT)
    allowed, retry_after = await record_flag_submission(redis, ip_hash)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="You have submitted too many flags recently.",
            headers={"Retry-After": str(retry_after)},
        )

    # Check review exists and is public
    review_result = await db.execute(
        select(Review).where(
            Review.id == review_id,
            Review.status.in_(["active", "cleared", "disputed"]),
        )
    )
    review = review_result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    # Server-side fingerprint hash
    server_fp_hash = hash_fingerprint(body.fingerprint_hash, settings.FINGERPRINT_SALT)

    # Check unique constraint (one flag per device per review)
    existing = await db.execute(
        select(Flag.id).where(
            Flag.review_id == review_id,
            Flag.fingerprint_hash == server_fp_hash,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="You have already flagged this review.")

    flag = Flag(
        review_id=review_id,
        reason=body.reason,
        fingerprint_hash=server_fp_hash,
    )
    db.add(flag)

    review.flag_count += 1
    if review.flag_count >= 3:
        review.status = "community_flagged"
        background_tasks.add_task(
            _recalculate_after_flag, review.plot_id
        )

    await db.commit()
    return {"detail": "Flag submitted."}


async def _recalculate_after_flag(plot_id: uuid.UUID):
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await recalculate_plot_score(plot_id, db)


@router.post("/{review_id}/disagree", status_code=201)
async def disagree_review(
    review_id: uuid.UUID,
    body: FlagSubmit,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Adds a disagree to a review (essentially a downvote). Uses the FlagSubmit schema to get fingerprint."""
    raw_ip = request.client.host if request.client else "0.0.0.0"
    redis = await get_redis()

    # Rate limit flags/disagrees together to prevent spam
    ip_hash = hash_ip(raw_ip, settings.IP_HASH_SALT)
    allowed, retry_after = await record_flag_submission(redis, ip_hash)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="You are performing this action too quickly.",
            headers={"Retry-After": str(retry_after)},
        )

    # Check review exists and is active
    review_result = await db.execute(
        select(Review).where(
            Review.id == review_id,
            Review.status.in_(["active", "cleared"]),
        )
    )
    review = review_result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    # Server-side fingerprint hash
    server_fp_hash = hash_fingerprint(body.fingerprint_hash, settings.FINGERPRINT_SALT)

    # To avoid creating a whole new tracking table for disagree votes, we just track disagreement 
    # as a specialized Flag type under the hood so we don't need a schema migration for the Flag table.
    existing = await db.execute(
        select(Flag.id).where(
            Flag.review_id == review_id,
            Flag.fingerprint_hash == server_fp_hash,
            Flag.reason == "disagree_vote"
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="You have already disagreed with this review.")

    # Log the disagree vote as a flag with a special reason
    flag = Flag(
        review_id=review_id,
        reason="disagree_vote",
        fingerprint_hash=server_fp_hash,
    )
    db.add(flag)

    review.disagree_count += 1
    await db.commit()
    
    return {"detail": "Disagreement registered.", "disagree_count": review.disagree_count}
