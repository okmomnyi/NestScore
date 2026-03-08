from fastapi import APIRouter

from app.services.csrf import generate_csrf_token


router = APIRouter(prefix="/api", tags=["Security"])


@router.get("/csrf")
async def get_csrf_token():
    """
    Issue a signed CSRF token for the client.
    The frontend must include this value as X-CSRF-Token on all
    state-changing API requests (POST/PUT/DELETE/PATCH).
    """
    token = generate_csrf_token()
    return {"csrf_token": token}

