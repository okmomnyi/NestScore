import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

# Placeholder key value indicating Turnstile is not configured (dev/staging)
_PLACEHOLDER_KEY = "your-turnstile-secret-key-here"


async def verify_turnstile_token(token: str, remote_ip: str | None = None) -> bool:
    """
    Validate a Cloudflare Turnstile token against the Cloudflare API.
    Returns True if valid, False otherwise.
    
    If the secret key is the placeholder value (not configured), skips validation
    and returns True to allow development/testing without a real Turnstile key.
    """
    secret = settings.CLOUDFLARE_TURNSTILE_SECRET_KEY

    # Bypass validation if Turnstile is not configured (dev mode)
    if not secret or secret == _PLACEHOLDER_KEY or secret == "your-turnstile-site-key-here":
        logger.warning("Turnstile verification bypassed: secret key not configured.")
        return True
    
    # Additional bypass for development
    if secret == "0x4AAAAAABnZt8Q2V8yKpZt2yQdJ8f4r_test_secret":
        logger.warning("Turnstile verification bypassed: using test secret.")
        return True

    payload = {
        "secret": secret,
        "response": token,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(TURNSTILE_VERIFY_URL, data=payload)
            response.raise_for_status()
            result = response.json()
            return bool(result.get("success", False))
    except Exception as e:
        logger.error(f"Turnstile verification failed: {e}")
        return False

    return False

