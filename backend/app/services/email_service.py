import asyncio
import logging
from datetime import datetime, timezone

import resend

from app.config import settings

logger = logging.getLogger(__name__)

resend.api_key = settings.RESEND_API_KEY

SENDER = "NestScore Community <noreply@nestscore.co.ke>"


async def send_admin_alert(subject: str, body: str) -> None:
    """Send an alert email to the admin address (anomaly detection, escalations)."""
    try:
        params: resend.Emails.SendParams = {
            "from": SENDER,
            "to": [settings.ADMIN_ALERT_EMAIL],
            "subject": subject,
            "text": body,
        }
        # resend.Emails.send() is synchronous — run in thread pool to avoid blocking the event loop
        await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Admin alert sent: {subject}")
    except Exception as e:
        logger.error(f"Failed to send admin alert: {e}")


async def send_landlord_verification(email: str, token: str, plot_name: str) -> None:
    """Send landlord claim verification email. Raw email is not stored."""
    try:
        params: resend.Emails.SendParams = {
            "from": SENDER,
            "to": [email],
            "subject": f"NestScore — Verify Your Claim for {plot_name}",
            "text": (
                f"Hello,\n\n"
                f"You requested to claim the listing for '{plot_name}' on NestScore.\n\n"
                f"Your verification token is:\n\n{token}\n\n"
                f"Submit this token via the platform to complete your claim.\n\n"
                f"If you did not request this, please ignore this email.\n\n"
                f"— NestScore Community\n"
                f"This email was sent to {email}. Your email address is not stored by NestScore."
            ),
        }
        # resend.Emails.send() is synchronous — run in thread pool to avoid blocking the event loop
        await asyncio.to_thread(resend.Emails.send, params)
        logger.info("Landlord verification email sent (address not logged)")
    except Exception as e:
        logger.error(f"Failed to send landlord verification email: {e}")


async def send_contact_forward(subject: str, message: str) -> None:
    """Forward a contact form submission to the admin."""
    try:
        params: resend.Emails.SendParams = {
            "from": SENDER,
            "to": [settings.ADMIN_ALERT_EMAIL],
            "subject": f"NestScore Contact Form: {subject}",
            "text": f"Contact form submission received at {datetime.now(timezone.utc).isoformat()}:\n\n{message}",
        }
        # resend.Emails.send() is synchronous — run in thread pool to avoid blocking the event loop
        await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Contact form forwarded to admin: {subject}")
    except Exception as e:
        logger.error(f"Failed to forward contact form: {e}")
