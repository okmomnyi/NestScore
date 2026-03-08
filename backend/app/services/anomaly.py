import logging
from datetime import datetime, timezone, timedelta
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plot import Plot
from app.models.review import Review
from app.models.audit_log import AuditLog
from app.services import email_service

logger = logging.getLogger(__name__)

RAPID_BURST_THRESHOLD = 5          # reviews per 30 minutes
RAPID_BURST_WINDOW_MINUTES = 30
SUBNET_CONCENTRATION_THRESHOLD = 0.60   # 60% same subnet
SCORE_JUMP_THRESHOLD = 1.5          # stars within 2 hours
SCORE_JUMP_WINDOW_HOURS = 2


async def run_anomaly_detection(plot_id: UUID, db: AsyncSession) -> None:
    """
    Run all three anomaly detection conditions for a plot.
    Any triggered condition sets plot.status = 'under_review'.
    """
    plot_result = await db.execute(select(Plot).where(Plot.id == plot_id))
    plot = plot_result.scalar_one_or_none()
    if not plot or plot.status == "under_review":
        return  # Already flagged or not found

    triggered = False
    trigger_condition = ""

    # --- Condition 1: Rapid burst ---
    window_start = datetime.now(timezone.utc) - timedelta(minutes=RAPID_BURST_WINDOW_MINUTES)
    burst_result = await db.execute(
        select(func.count(Review.id)).where(
            Review.plot_id == plot_id,
            Review.created_at >= window_start,
        )
    )
    burst_count = burst_result.scalar_one()
    if burst_count > RAPID_BURST_THRESHOLD:
        triggered = True
        trigger_condition = f"rapid_burst: {burst_count} reviews in {RAPID_BURST_WINDOW_MINUTES} minutes"

    # --- Condition 2: IP subnet concentration ---
    if not triggered:
        subnet_result = await db.execute(
            select(Review.subnet_prefix_hash, func.count(Review.id).label("cnt"))
            .where(Review.plot_id == plot_id)
            .group_by(Review.subnet_prefix_hash)
        )
        subnet_rows = subnet_result.all()
        total_reviews = sum(r.cnt for r in subnet_rows)
        if total_reviews > 0:
            for row in subnet_rows:
                if row.cnt / total_reviews > SUBNET_CONCENTRATION_THRESHOLD:
                    triggered = True
                    pct_value = 100.0 * row.cnt / total_reviews
                    trigger_condition = f"subnet_concentration: {pct_value:.1f}% of reviews from same subnet"
                    break

    # --- Condition 3: Score jump ---
    if not triggered and plot.last_score_snapshot is not None and plot.last_snapshot_at is not None:
        # last_snapshot_at is a tz-aware datetime from the DB (DateTime(timezone=True))
        # Do NOT call .replace(tzinfo=...) on it — that would overwrite an existing tz.
        snapshot_at = plot.last_snapshot_at
        if snapshot_at.tzinfo is None:
            # Defensive: handle a naive datetime from a non-tz-aware DB column gracefully
            snapshot_at = snapshot_at.replace(tzinfo=timezone.utc)
        snapshot_age = datetime.now(timezone.utc) - snapshot_at
        if snapshot_age <= timedelta(hours=SCORE_JUMP_WINDOW_HOURS):
            if plot.weighted_score is not None:
                diff = abs(float(plot.weighted_score) - float(plot.last_score_snapshot))
                if diff > SCORE_JUMP_THRESHOLD:
                    triggered = True
                    trigger_condition = (
                        f"score_jump: {float(plot.last_score_snapshot):.2f} → "
                        f"{float(plot.weighted_score):.2f} within {SCORE_JUMP_WINDOW_HOURS}h"
                    )

    if triggered:
        plot.status = "under_review"

        # Log to audit_log
        audit = AuditLog(
            admin_action="anomaly_detected",
            target_type="plot",
            target_id=plot_id,
            note=trigger_condition,
        )
        db.add(audit)
        await db.commit()

        pid_str = str(plot_id).split("-")[0]
        logger.warning(f"Anomaly detected for plot {pid_str}: {trigger_condition}")

        # Send admin email alert
        try:
            await email_service.send_admin_alert(
                subject=f"NestScore Anomaly Alert — {plot.name}",
                body=(
                    f"Anomaly detected on plot: {plot.name}\n"
                    f"Condition: {trigger_condition}\n\n"
                    f"Please review the submission queue in the admin dashboard."
                ),
            )
        except Exception as e:
            logger.error(f"Failed to send anomaly alert email: {e}")
    else:
        # Update score snapshot for next comparison
        if plot.weighted_score is not None:
            plot.last_score_snapshot = plot.weighted_score
            plot.last_snapshot_at = datetime.now(timezone.utc)
            await db.commit()
