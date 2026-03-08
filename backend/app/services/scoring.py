import logging
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plot import Plot
from app.models.review import Review
from app.config import settings

logger = logging.getLogger(__name__)

# Status values that qualify a review to count toward score
QUALIFYING_STATUSES = ("active", "cleared", "disputed")

# M constant — minimum vote threshold (configurable in config.py)
M = settings.BAYESIAN_M


async def recalculate_plot_score(plot_id: str, db: AsyncSession) -> None:
    """
    Recalculate Bayesian weighted score for a single plot.
    Formula: weighted_score = (v / (v + m)) * R + (m / (v + m)) * C
    """
    # Fetch all qualifying reviews for this plot
    result = await db.execute(
        select(Review.stars, Review.rating_weight)
        .where(
            Review.plot_id == plot_id,
            Review.status.in_(QUALIFYING_STATUSES),
        )
    )
    reviews = result.all()

    if not reviews:
        # No qualifying reviews — reset scores
        plot_result = await db.execute(select(Plot).where(Plot.id == plot_id))
        plot = plot_result.scalar_one_or_none()
        if plot:
            plot.weighted_score = None
            plot.raw_avg = None
            plot.total_ratings = 0
            await db.commit()
        return

    # Calculate weighted average R for this plot
    total_weight = sum(float(r.rating_weight) for r in reviews)
    if total_weight == 0:
        total_weight = len(reviews)

    weighted_sum = sum(float(r.stars) * float(r.rating_weight) for r in reviews)
    R = weighted_sum / total_weight
    raw_avg = sum(r.stars for r in reviews) / len(reviews)
    v = len(reviews)

    # Calculate global mean C across all plots with at least 1 qualifying review
    global_result = await db.execute(
        select(Review.stars, Review.rating_weight, Review.plot_id)
        .where(Review.status.in_(QUALIFYING_STATUSES))
    )
    all_qualifying = global_result.all()

    if all_qualifying:
        global_total_weight = sum(float(r.rating_weight) for r in all_qualifying)
        if global_total_weight == 0:
            global_total_weight = len(all_qualifying)
        C = sum(float(r.stars) * float(r.rating_weight) for r in all_qualifying) / global_total_weight
    else:
        C = 3.0  # Neutral fallback

    # Bayesian formula
    m = M
    weighted_score = (v / (v + m)) * R + (m / (v + m)) * C

    # Clamp to valid range
    weighted_score = max(1.0, min(5.0, weighted_score))

    plot_result = await db.execute(select(Plot).where(Plot.id == plot_id))
    plot = plot_result.scalar_one_or_none()
    if plot:
        w_score_f = float(weighted_score)
        r_avg_f = float(raw_avg)
        plot.weighted_score = Decimal(f"{w_score_f:.2f}")
        plot.raw_avg = Decimal(f"{r_avg_f:.2f}")
        plot.total_ratings = v
        await db.commit()

    p_id_str = str(plot_id).split("-")[0]
    logger.info(f"Recalculated score for plot {p_id_str}: {weighted_score:.2f}")
