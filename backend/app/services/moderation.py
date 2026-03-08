"""
Moderation service — AI scoring removed.

Previously used Google Gemini 2.0 Flash to score reviews for quality and toxicity.
AI scoring has been removed. Reviews are published based on time only (20-minute delay),
and the profanity filter + community flagging system handles quality control.

This module is kept as a no-op stub so any code that still imports it does not break.
"""
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def score_review(review_id: UUID, db: AsyncSession) -> None:
    """
    No-op stub. AI scoring removed.
    Reviews are published after publish_at elapses with no AI gate.
    Profanity filter and community flagging remain active.
    """
    r_id_str = str(review_id).split("-")[0]
    logger.debug(
        "Moderation service called for review %s — AI scoring disabled, no action taken.",
        r_id_str,
    )
