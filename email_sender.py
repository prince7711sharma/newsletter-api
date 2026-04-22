"""
email_sender.py - Email delivery via Resend API with retry logic
"""

import logging
import time
from typing import Optional

import resend

from config import settings

logger = logging.getLogger(__name__)

resend.api_key = settings.RESEND_API_KEY


def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    html_body: str,
    retries: int = settings.MAX_EMAIL_RETRIES,
) -> bool:
    """
    Send an HTML email via Resend with exponential back-off retry.
    Returns True on success, False after all retries fail.
    """
    attempt = 0
    delay = settings.RETRY_DELAY

    while attempt < retries:
        attempt += 1
        try:
            params: resend.Emails.SendParams = {
                "from": settings.EMAIL_FROM,
                "to": [to_email],
                "subject": subject,
                "html": html_body,
                "reply_to": settings.EMAIL_FROM,
                "headers": {
                    "X-Entity-Ref-ID": f"newsletter-{to_email}",
                    "List-Unsubscribe": (
                        f"<{settings.BASE_URL}/unsubscribe?email={to_email}>"
                    ),
                },
            }
            response = resend.Emails.send(params)
            email_id = getattr(response, "id", "N/A")
            logger.info(
                f"✅ Email sent to {to_email} | "
                f"ID: {email_id} | Attempt: {attempt}"
            )
            return True

        except resend.exceptions.ResendError as e:
            logger.warning(
                f"⚠️ Resend error for {to_email} "
                f"(attempt {attempt}/{retries}): {e}"
            )
        except Exception as e:
            logger.error(
                f"❌ Unexpected error sending to {to_email} "
                f"(attempt {attempt}/{retries}): {e}"
            )

        if attempt < retries:
            logger.info(f"🔄 Retrying in {delay:.1f}s...")
            time.sleep(delay)
            delay *= 2  # Exponential back-off

    logger.error(f"💀 All {retries} attempts failed for {to_email}.")
    return False
