import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review

logger = logging.getLogger(__name__)


async def check_duplicate_review(
    fingerprint_hash: str, plot_id: UUID, db: AsyncSession
) -> bool:
    """
    Returns True if a review with this fingerprint_hash already exists for this plot.
    The unique constraint is also enforced at the database level.
    """
    result = await db.execute(
        select(Review.id).where(
            Review.fingerprint_hash == fingerprint_hash,
            Review.plot_id == plot_id,
        )
    )
    return result.scalar_one_or_none() is not None
