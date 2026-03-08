import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.services.hashing import hash_ip
from app.config import settings

logger = logging.getLogger("nestscore.audit")


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Logs every request using ONLY hashed identifiers — never raw IPs, emails, or fingerprints.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.time()
        raw_ip = request.client.host if request.client else "unknown"

        # Hash the IP immediately — never log the raw value
        ip_hash_short = hash_ip(raw_ip, settings.IP_HASH_SALT)[:12]

        response = await call_next(request)

        duration_ms = int((time.time() - start) * 1000)
        logger.info(
            f"{request.method} {request.url.path} {response.status_code} "
            f"ip={ip_hash_short}... {duration_ms}ms"
        )
        return response
