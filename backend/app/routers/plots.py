import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.dispute import Dispute
from app.models.plot import Plot
from app.models.review import Review
from app.redis_client import get_redis
from app.schemas.plot import PlotListResponse, PlotMapResponse, PlotResponse
from app.schemas.review import ReviewPublicResponse, ReviewListResponse

router = APIRouter(prefix="/api/plots", tags=["Plots"])


@router.get("", response_model=PlotListResponse)
async def list_plots(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    area: Optional[str] = None,
    min_stars: Optional[float] = Query(None, ge=1, le=5),
    db: AsyncSession = Depends(get_db),
):
    query = select(Plot).where(Plot.status == "active")
    count_query = select(func.count(Plot.id)).where(Plot.status == "active")

    if area and area != "All":
        query = query.where(Plot.area == area)
        count_query = count_query.where(Plot.area == area)
    if min_stars is not None:
        query = query.where(Plot.weighted_score >= min_stars)
        count_query = count_query.where(Plot.weighted_score >= min_stars)

    query = query.order_by(Plot.weighted_score.desc().nulls_last())

    total_result = await db.execute(count_query)
    total_count = total_result.scalar_one()

    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    plots = result.scalars().all()

    return PlotListResponse(
        plots=[PlotResponse.model_validate(p) for p in plots],
        total_count=total_count,
        page=page,
        per_page=per_page,
    )


@router.get("/map", response_model=list[PlotMapResponse])
async def get_map_plots(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    cache_key = "cache:plots:map"

    # Try to read from Redis cache first
    try:
        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            return [PlotMapResponse(**p) for p in data]
    except Exception:
        redis = None  # Redis unavailable, skip caching

    result = await db.execute(
        select(
            Plot.id,
            Plot.name,
            Plot.area,
            Plot.gps_lat,
            Plot.gps_lng,
            Plot.weighted_score,
            Plot.total_ratings,
            Plot.status,
        ).where(Plot.status.in_(["active", "under_review"]))
    )
    rows = result.all()

    plots = [
        PlotMapResponse(
            id=r.id,
            name=r.name,
            area=r.area,
            gps_lat=r.gps_lat,
            gps_lng=r.gps_lng,
            weighted_score=r.weighted_score,
            total_ratings=r.total_ratings,
            status=r.status,
        )
        for r in rows
    ]

    # Cache for 60 seconds if Redis is available
    try:
        if redis:
            await redis.setex(cache_key, 60, json.dumps([p.model_dump(mode="json") for p in plots]))
    except Exception:
        pass  # Redis unavailable, skip caching

    return plots


@router.get("/{plot_id}", response_model=dict)
async def get_plot(
    plot_id: uuid.UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    plot_result = await db.execute(select(Plot).where(Plot.id == plot_id))
    plot = plot_result.scalar_one_or_none()
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    # Public reviews: active, cleared, disputed
    reviews_query = (
        select(Review)
        .where(
            Review.plot_id == plot_id,
            Review.status.in_(["active", "cleared", "disputed"]),
        )
        .order_by(Review.publish_at.desc())
    )

    count_result = await db.execute(
        select(func.count(Review.id)).where(
            Review.plot_id == plot_id,
            Review.status.in_(["active", "cleared", "disputed"]),
        )
    )
    total_count = count_result.scalar_one()

    offset = (page - 1) * per_page
    reviews_result = await db.execute(reviews_query.offset(offset).limit(per_page))
    reviews = reviews_result.scalars().all()

    # For disputed reviews attach the landlord response
    review_responses = []
    for r in reviews:
        dispute_response = None
        if r.status == "disputed":
            d_result = await db.execute(
                select(Dispute.landlord_response_text)
                .where(Dispute.review_id == r.id)
                .limit(1)
            )
            d_row = d_result.scalar_one_or_none()
            if d_row:
                dispute_response = d_row
        review_responses.append(
            ReviewPublicResponse(
                id=r.id,
                stars=r.stars,
                comment_text=r.comment_text,
                nickname=r.nickname,
                status=r.status,
                flag_count=r.flag_count,
                disagree_count=r.disagree_count,
                publish_at=r.publish_at,
                created_at=r.created_at,
                dispute_response=dispute_response,
            )
        )

    return {
        "plot": PlotResponse.model_validate(plot),
        "reviews": ReviewListResponse(
            reviews=review_responses,
            total_count=total_count,
            page=page,
            per_page=per_page,
        ),
    }
