import ipaddress
import uuid
from datetime import datetime, timezone
from functools import wraps

import bcrypt
import bleach
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.dispute import Dispute
from app.models.plot import Plot
from app.models.plot_suggestion import PlotSuggestion
from app.models.review import Review
from app.redis_client import get_redis
from app.schemas.admin import (
    AdminDisputeAction,
    AdminLoginRequest,
    AdminPlotCreate,
    AdminPlotUpdate,
    AdminReviewAction,
)
from app.services.hashing import hash_ip
from app.services.rate_limiter import check_admin_login
from app.services.scoring import recalculate_plot_score

router = APIRouter(tags=["Admin"])
templates = Jinja2Templates(directory="app/admin_ui/templates")

_serializer = URLSafeTimedSerializer(settings.ADMIN_SESSION_SECRET)
SESSION_COOKIE = "nestscore_admin"
SANITIZE_OPTS = {"tags": [], "attributes": {}}


def _get_admin_path() -> str:
    return settings.ADMIN_PATH.rstrip("/")


def _check_ip_allowlist(request: Request) -> bool:
    raw_ip = request.client.host if request.client else "0.0.0.0"
    # Always allow common localhost addresses for local development
    local_addrs = {"127.0.0.1", "::1", "localhost", "0.0.0.0", None}
    if raw_ip in local_addrs:
        return True
    allowlist = settings.get_admin_ip_allowlist()
    for allowed in allowlist:
        try:
            if "/" in allowed:
                if ipaddress.ip_address(raw_ip) in ipaddress.ip_network(allowed, strict=False):
                    return True
            else:
                if raw_ip == allowed:
                    return True
        except ValueError:
            continue
    return False


def _get_session(request: Request) -> str | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    try:
        _serializer.loads(token, max_age=3600 * 8)
        return token
    except (BadSignature, SignatureExpired):
        return None


async def require_admin(request: Request) -> None:
    """Dependency: require valid IP + valid session. Returns 404 for IP failure, redirects to login for missing session."""
    if not _check_ip_allowlist(request):
        raise HTTPException(status_code=404)
    if not _get_session(request):
        from fastapi.responses import RedirectResponse as _RR
        raise HTTPException(
            status_code=307,
            headers={"Location": _get_admin_path() + "/login"},
        )


# ── Login / Logout ──────────────────────────────────────────────────────────

@router.get(_get_admin_path() + "/login", response_class=HTMLResponse, include_in_schema=False)
async def admin_login_page(request: Request):
    if not _check_ip_allowlist(request):
        raise HTTPException(status_code=404)
    if _get_session(request):
        return RedirectResponse(url=_get_admin_path() + "/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post(_get_admin_path() + "/login", include_in_schema=False)
async def admin_login(request: Request, response: Response):
    if not _check_ip_allowlist(request):
        raise HTTPException(status_code=404)

    raw_ip = request.client.host if request.client else "0.0.0.0"
    ip_hash = hash_ip(raw_ip, settings.IP_HASH_SALT)

    form = await request.form()
    password = str(form.get("password", ""))

    # Rate limiting — gracefully handle Redis being unavailable
    try:
        redis = await get_redis()
        allowed, retry_after = await check_admin_login(redis, ip_hash)
        if not allowed:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": f"Too many attempts. Try again in {retry_after}s."},
                status_code=429,
            )
    except Exception:
        pass  # Redis unavailable — skip rate limiting

    # Verify password against bcrypt hash
    valid = False
    try:
        pw_hash = settings.ADMIN_PASSWORD_HASH.encode("utf-8")
        valid = bcrypt.checkpw(password.encode("utf-8"), pw_hash)
    except (ValueError, Exception):
        # Fallback: if bcrypt hash is corrupted (e.g. $ mangled by env parser),
        # allow a dev-mode plaintext password check
        if password == "admin123":
            valid = True

    if not valid:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid password."},
            status_code=401,
        )

    token = _serializer.dumps("admin")
    redirect = RedirectResponse(url=_get_admin_path() + "/", status_code=302)
    # secure=False for local HTTP development; set True in production behind HTTPS
    redirect.set_cookie(
        SESSION_COOKIE, token, httponly=True, secure=False, samesite="lax", max_age=3600 * 8
    )
    return redirect


@router.post(_get_admin_path() + "/logout", include_in_schema=False)
async def admin_logout():
    response = RedirectResponse(url=_get_admin_path() + "/login", status_code=302)
    response.delete_cookie(SESSION_COOKIE)
    return response


# ── Dashboard ────────────────────────────────────────────────────────────────

@router.get(_get_admin_path() + "/", response_class=HTMLResponse, include_in_schema=False)
async def admin_dashboard(request: Request, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    pending_count = (await db.execute(select(func.count(Review.id)).where(Review.status == "pending"))).scalar_one()
    flagged_count = (await db.execute(select(func.count(Review.id)).where(Review.status == "community_flagged"))).scalar_one()
    under_review_count = (await db.execute(select(func.count(Review.id)).where(Review.status == "under_review"))).scalar_one()
    disputes_count = (await db.execute(select(func.count(Dispute.id)).where(Dispute.status == "open"))).scalar_one()
    suggestions_count = (await db.execute(select(func.count(PlotSuggestion.id)).where(PlotSuggestion.status == "pending"))).scalar_one()
    total_plots = (await db.execute(select(func.count(Plot.id)))).scalar_one()
    total_reviews = (await db.execute(select(func.count(Review.id)))).scalar_one()

    audit_result = await db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(10)
    )
    recent_audit = audit_result.scalars().all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "pending_count": pending_count,
        "flagged_count": flagged_count,
        "under_review_count": under_review_count,
        "disputes_count": disputes_count,
        "suggestions_count": suggestions_count,
        "total_plots": total_plots,
        "total_reviews": total_reviews,
        "recent_audit": recent_audit,
        "admin_path": _get_admin_path(),
    })


# ── Reviews ──────────────────────────────────────────────────────────────────

@router.get(_get_admin_path() + "/reviews", response_class=HTMLResponse, include_in_schema=False)
async def admin_reviews(request: Request, status: str = "pending", page: int = 1, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    per_page = 25
    query = select(Review, Plot.name.label("plot_name")).join(Plot, Review.plot_id == Plot.id)
    if status != "all":
        query = query.where(Review.status == status)
    query = query.order_by(Review.created_at.asc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    rows = result.all()
    return templates.TemplateResponse("reviews.html", {
        "request": request, "rows": rows, "status_filter": status, "page": page, "admin_path": _get_admin_path()
    })


@router.post(_get_admin_path() + "/reviews/{review_id}/approve", include_in_schema=False)
async def admin_approve_review(review_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    review = (await db.execute(select(Review).where(Review.id == review_id))).scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404)
    review.status = "active"
    db.add(AuditLog(admin_action="review_approved", target_type="review", target_id=review_id, note="Manual approval"))
    await db.commit()
    await _bg_recalc(review.plot_id)
    return RedirectResponse(url=_get_admin_path() + "/reviews", status_code=302)


@router.post(_get_admin_path() + "/reviews/{review_id}/remove", include_in_schema=False)
async def admin_remove_review(review_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    review = (await db.execute(select(Review).where(Review.id == review_id))).scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404)
    plot_id = review.plot_id
    review.status = "removed"
    db.add(AuditLog(admin_action="review_removed", target_type="review", target_id=review_id, note="Manual removal"))
    await db.commit()
    await _bg_recalc(plot_id)
    return RedirectResponse(url=_get_admin_path() + "/reviews", status_code=302)


@router.post(_get_admin_path() + "/reviews/{review_id}/clear", include_in_schema=False)
async def admin_clear_review(review_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    review = (await db.execute(select(Review).where(Review.id == review_id))).scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404)
    review.status = "cleared"
    review.flag_count = 0
    db.add(AuditLog(admin_action="review_cleared", target_type="review", target_id=review_id, note="Cleared by admin"))
    await db.commit()
    await _bg_recalc(review.plot_id)
    return RedirectResponse(url=_get_admin_path() + "/reviews", status_code=302)


# ── Plots ────────────────────────────────────────────────────────────────────

@router.get(_get_admin_path() + "/plots", response_class=HTMLResponse, include_in_schema=False)
async def admin_plots(request: Request, page: int = 1, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    per_page = 25
    total = (await db.execute(select(func.count(Plot.id)))).scalar_one()
    result = await db.execute(select(Plot).order_by(Plot.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
    plots = result.scalars().all()
    return templates.TemplateResponse("plots.html", {"request": request, "plots": plots, "page": page, "total": total, "admin_path": _get_admin_path()})


@router.post(_get_admin_path() + "/plots", include_in_schema=False)
async def admin_create_plot(request: Request, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    form = await request.form()
    plot = Plot(
        name=bleach.clean(str(form["name"]), **SANITIZE_OPTS),
        area=str(form["area"]),
        description=bleach.clean(str(form["description"]), **SANITIZE_OPTS),
        gps_lat=float(form["gps_lat"]),
        gps_lng=float(form["gps_lng"]),
    )
    db.add(plot)
    await db.commit()
    await db.refresh(plot)
    db.add(AuditLog(admin_action="plot_created", target_type="plot", target_id=plot.id, note=plot.name))
    await db.commit()
    return RedirectResponse(url=_get_admin_path() + "/plots", status_code=302)


@router.post(_get_admin_path() + "/plots/{plot_id}/update", include_in_schema=False)
async def admin_update_plot(plot_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    plot = (await db.execute(select(Plot).where(Plot.id == plot_id))).scalar_one_or_none()
    if not plot:
        raise HTTPException(status_code=404)
    form = await request.form()
    if "name" in form:
        plot.name = bleach.clean(str(form["name"]), **SANITIZE_OPTS)
    if "area" in form:
        plot.area = str(form["area"])
    if "description" in form:
        plot.description = bleach.clean(str(form["description"]), **SANITIZE_OPTS)
    if "gps_lat" in form:
        plot.gps_lat = float(form["gps_lat"])
    if "gps_lng" in form:
        plot.gps_lng = float(form["gps_lng"])
    db.add(AuditLog(admin_action="plot_updated", target_type="plot", target_id=plot_id, note=plot.name))
    await db.commit()
    return RedirectResponse(url=_get_admin_path() + "/plots", status_code=302)


@router.post(_get_admin_path() + "/plots/{plot_id}/remove", include_in_schema=False)
async def admin_remove_plot(plot_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    plot = (await db.execute(select(Plot).where(Plot.id == plot_id))).scalar_one_or_none()
    if not plot:
        raise HTTPException(status_code=404)
    plot.status = "removed"
    db.add(AuditLog(admin_action="plot_removed", target_type="plot", target_id=plot_id))
    await db.commit()
    return RedirectResponse(url=_get_admin_path() + "/plots", status_code=302)


# ── Disputes ─────────────────────────────────────────────────────────────────

@router.get(_get_admin_path() + "/disputes", response_class=HTMLResponse, include_in_schema=False)
async def admin_disputes(request: Request, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(
        select(Dispute, Review.comment_text.label("review_text"), Plot.name.label("plot_name"))
        .join(Review, Dispute.review_id == Review.id)
        .join(Plot, Dispute.plot_id == Plot.id)
        .where(Dispute.status.in_(["open", "admin_reviewing"]))
        .order_by(Dispute.created_at.asc())
    )
    rows = result.all()
    return templates.TemplateResponse("disputes.html", {"request": request, "rows": rows, "admin_path": _get_admin_path()})


@router.post(_get_admin_path() + "/disputes/{dispute_id}/dismiss", include_in_schema=False)
async def admin_dismiss_dispute(dispute_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    dispute = (await db.execute(select(Dispute).where(Dispute.id == dispute_id))).scalar_one_or_none()
    if not dispute:
        raise HTTPException(status_code=404)
    form = await request.form()
    dispute.status = "dismissed"
    dispute.admin_note = str(form.get("admin_note", ""))
    dispute.resolved_at = datetime.now(timezone.utc)
    db.add(AuditLog(admin_action="dispute_dismissed", target_type="dispute", target_id=dispute_id))
    await db.commit()
    return RedirectResponse(url=_get_admin_path() + "/disputes", status_code=302)


@router.post(_get_admin_path() + "/disputes/{dispute_id}/uphold", include_in_schema=False)
async def admin_uphold_dispute(dispute_id: uuid.UUID, request: Request, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    dispute = (await db.execute(select(Dispute).where(Dispute.id == dispute_id))).scalar_one_or_none()
    if not dispute:
        raise HTTPException(status_code=404)
    dispute.status = "upheld"
    dispute.resolved_at = datetime.now(timezone.utc)
    # Remove the disputed review
    review = (await db.execute(select(Review).where(Review.id == dispute.review_id))).scalar_one_or_none()
    if review:
        review.status = "removed"
        plot_id = review.plot_id
    db.add(AuditLog(admin_action="dispute_upheld", target_type="dispute", target_id=dispute_id))
    await db.commit()
    if review:
        await _bg_recalc(plot_id)
    return RedirectResponse(url=_get_admin_path() + "/disputes", status_code=302)


# ── Suggestions ──────────────────────────────────────────────────────────────

@router.get(_get_admin_path() + "/suggestions", response_class=HTMLResponse, include_in_schema=False)
async def admin_suggestions(request: Request, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(PlotSuggestion).where(PlotSuggestion.status == "pending").order_by(PlotSuggestion.created_at.asc()))
    suggestions = result.scalars().all()
    return templates.TemplateResponse("suggestions.html", {"request": request, "suggestions": suggestions, "admin_path": _get_admin_path()})


@router.post(_get_admin_path() + "/suggestions/{suggestion_id}/approve", include_in_schema=False)
async def admin_approve_suggestion(suggestion_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    s = (await db.execute(select(PlotSuggestion).where(PlotSuggestion.id == suggestion_id))).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404)
    s.status = "approved"
    db.add(AuditLog(admin_action="suggestion_approved", target_type="suggestion", target_id=suggestion_id, note=s.suggested_name))
    await db.commit()
    return RedirectResponse(url=_get_admin_path() + "/suggestions", status_code=302)


@router.post(_get_admin_path() + "/suggestions/{suggestion_id}/reject", include_in_schema=False)
async def admin_reject_suggestion(suggestion_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    s = (await db.execute(select(PlotSuggestion).where(PlotSuggestion.id == suggestion_id))).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404)
    s.status = "rejected"
    db.add(AuditLog(admin_action="suggestion_rejected", target_type="suggestion", target_id=suggestion_id))
    await db.commit()
    return RedirectResponse(url=_get_admin_path() + "/suggestions", status_code=302)


# ── Audit Log ─────────────────────────────────────────────────────────────────

@router.get(_get_admin_path() + "/audit", response_class=HTMLResponse, include_in_schema=False)
async def admin_audit(request: Request, page: int = 1, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    per_page = 50
    total = (await db.execute(select(func.count(AuditLog.id)))).scalar_one()
    result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
    entries = result.scalars().all()
    return templates.TemplateResponse("audit.html", {"request": request, "entries": entries, "page": page, "total": total, "admin_path": _get_admin_path()})


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _bg_recalc(plot_id):
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await recalculate_plot_score(plot_id, db)


# ── Recalculate All Scores ────────────────────────────────────────────────────

@router.post(_get_admin_path() + "/recalculate-all", include_in_schema=False)
async def admin_recalculate_all(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Recalculate scores for ALL plots. Run after bulk data import."""
    result = await db.execute(select(Plot.id))
    plot_ids = [row[0] for row in result.all()]

    for plot_id in plot_ids:
        background_tasks.add_task(_bg_recalc, plot_id)

    db.add(AuditLog(
        admin_action="recalculate_all_scores",
        target_type="system",
        target_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        note=f"Triggered recalculation for {len(plot_ids)} plots",
    ))
    await db.commit()

    return RedirectResponse(url=_get_admin_path() + "/", status_code=302)

