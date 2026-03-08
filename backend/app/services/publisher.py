import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.review import Review

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def publish_pending_reviews() -> None:
    """
    Runs every 5 minutes.
    Queries pending reviews with publish_at <= now().
    Sets qualifying reviews to active, recalculates plot score, triggers anomaly check.

    AI scoring has been removed — reviews are no longer gated on ai_quality_score.
    The profanity filter at submission time and community flagging handle quality control.
    """
    from app.services.scoring import recalculate_plot_score
    from app.services.anomaly import run_anomaly_detection

    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Review).where(
                Review.status == "pending",
                Review.publish_at <= now,
            )
        )
        reviews = result.scalars().all()

        if not reviews:
            return

        logger.info(f"Publisher: activating {len(reviews)} reviews")

        affected_plot_ids = set()
        for review in reviews:
            review.status = "active"
            affected_plot_ids.add(review.plot_id)

        await db.commit()

        # Recalculate scores and run anomaly detection per plot
        for plot_id in affected_plot_ids:
            async with AsyncSessionLocal() as score_db:
                await recalculate_plot_score(plot_id, score_db)
            async with AsyncSessionLocal() as anomaly_db:
                await run_anomaly_detection(plot_id, anomaly_db)


def start_scheduler() -> None:
    scheduler.add_job(
        publish_pending_reviews,
        trigger="interval",
        minutes=5,
        id="publish_pending_reviews",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler started — publish job every 5 minutes")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped")
