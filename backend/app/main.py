from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.middleware.audit import AuditLogMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.csrf import CSRFMiddleware
from app.redis_client import close_redis, get_redis
from app.routers import admin, disputes, health, plots, reviews, security
from app.services.publisher import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await get_redis()
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()
    await close_redis()


app = FastAPI(
    title="NestScore API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter

# ── Middleware ───────────────────────────────────────────────────────────────
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuditLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://nestscore.co.ke"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# ── Custom Error Handlers ("No as a Service") ────────────────────────────────
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import random

NO_REASONS = [
    "I'm holding up a scorecard that says 0, as in 0% chance.",
    "My sources say no.",
    "Forget about it.",
    "Not in a million years.",
    "I'd rather not.",
    "Computers say no.",
    "Negative.",
    "Absolutely not.",
    "No.",
    "Access Denied. Reason: No."
]

@app.exception_handler(404)
async def custom_404_handler(request, __):
    return JSONResponse(
        status_code=404,
        content={"answer": "no", "reason": random.choice(NO_REASONS)}
    )

@app.exception_handler(401)
async def custom_401_handler(request, __):
    return JSONResponse(
        status_code=401,
        content={"answer": "no", "reason": "Unauthorized. " + random.choice(NO_REASONS)}
    )

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(security.router)
app.include_router(plots.router)
app.include_router(reviews.router)
app.include_router(disputes.router)
app.include_router(admin.router)
