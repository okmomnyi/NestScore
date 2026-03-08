import uuid

import bleach
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.dispute import Dispute
from app.models.review import Review
from app.redis_client import get_redis
from app.schemas.dispute import ContactForm, DisputeSubmit
from app.services import email_service, turnstile
from app.services.rate_limiter import record_contact_submission
from app.services.hashing import hash_ip
from app.config import settings

router = APIRouter(prefix="/api", tags=["Disputes & Contact"])

SANITIZE_OPTS = {"tags": [], "attributes": {}}


@router.post("/disputes", status_code=201)
async def submit_dispute(
    body: DisputeSubmit,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a plain reply to a review.
    No email verification token required.
    """
    raw_ip = request.client.host if request.client else "0.0.0.0"
    
    # Verify review exists and is active
    review_result = await db.execute(
        select(Review).where(
            Review.id == body.review_id,
            Review.plot_id == body.plot_id,
            Review.status.in_(["active", "cleared", "disputed"]),
        )
    )
    review = review_result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    # Check if a reply already exists (only 1 reply allowed per review for now)
    existing_reply = await db.execute(
        select(Dispute.id).where(Dispute.review_id == body.review_id)
    )
    if existing_reply.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="This review has already been replied to.")

    clean_response = bleach.clean(body.landlord_response_text, **SANITIZE_OPTS)

    # Note: We reuse the Dispute model, but conceptually this is just a 'Reply'.
    # We DO NOT change the review's status to 'disputed' — it stays 'active' and visible.
    dispute = Dispute(
        review_id=body.review_id,
        plot_id=body.plot_id,
        landlord_response_text=clean_response,
        status="open",
        # We don't change the review status here like we used to
    )
    db.add(dispute)
    await db.commit()
    await db.refresh(dispute)

    return {"id": str(dispute.id), "status": "published", "message": "Reply published successfully."}


@router.post("/contact")
async def submit_contact(
    body: ContactForm,
    request: Request,
    background_tasks: BackgroundTasks,
):
    raw_ip = request.client.host if request.client else "0.0.0.0"
    redis = await get_redis()

    # Rate limit: 5 per IP per hour
    ip_hash = hash_ip(raw_ip, settings.IP_HASH_SALT)
    allowed, retry_after = await record_contact_submission(redis, ip_hash)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many contact submissions. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    # Validate Turnstile
    valid = await turnstile.verify_turnstile_token(body.turnstile_token, raw_ip)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid CAPTCHA token.")

    clean_subject = bleach.clean(body.subject, **SANITIZE_OPTS)
    clean_message = bleach.clean(body.message, **SANITIZE_OPTS)

    # Forward to admin — no DB storage
    background_tasks.add_task(
        email_service.send_contact_forward,
        clean_subject,
        clean_message,
    )

    return {"detail": "Your message has been sent. We will respond through the NestScore platform if needed."}
