"""
email_sender.py - Email delivery via Gmail SMTP with retry logic
"""

import logging
import smtplib
import time
import httpx
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    html_body: str,
    retries: int = settings.MAX_EMAIL_RETRIES,
) -> bool:
    """
    Send an HTML email via Resend API (HTTP) or Gmail SMTP (Fallback) with retry.
    Returns True on success, False after all retries fail.
    """
    attempt = 0
    delay = settings.RETRY_DELAY

    while attempt < retries:
        attempt += 1
        try:
            if settings.RESEND_API_KEY:
                # ─── Option 1: Resend HTTP API (Works on Render) ───
                logger.info(f"🚀 Using Resend API for {to_email}...")
                payload = {
                    "from": settings.EMAIL_FROM,
                    "to": [to_email],
                    "subject": subject,
                    "html": html_body,
                    "headers": {
                        "X-Entity-Ref-ID": f"newsletter-{to_email}",
                        "List-Unsubscribe": f"<{settings.BASE_URL}/unsubscribe?email={to_email}>"
                    }
                }
                
                with httpx.Client() as client:
                    response = client.post(
                        "https://api.resend.com/emails",
                        headers={
                            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json=payload,
                        timeout=15.0
                    )
                
                if response.status_code >= 400:
                    raise Exception(f"Resend API Error {response.status_code}: {response.text}")

            else:
                # ─── Option 2: Gmail SMTP (Fails on Render Free Tier, works locally) ───
                logger.info(f"🐌 No Resend key found. Falling back to Gmail SMTP for {to_email}...")
                msg = MIMEMultipart()
                msg["From"] = settings.EMAIL_FROM
                msg["To"] = to_email
                msg["Subject"] = subject
                msg["X-Entity-Ref-ID"] = f"newsletter-{to_email}"
                msg["List-Unsubscribe"] = f"<{settings.BASE_URL}/unsubscribe?email={to_email}>"
                msg.attach(MIMEText(html_body, "html"))

                with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.send_message(msg)

            logger.info(f"✅ Email sent to {to_email} | Attempt: {attempt}")
            return True

        except Exception as e:
            logger.warning(
                f"⚠️ Email error for {to_email} "
                f"(attempt {attempt}/{retries}): {e}"
            )

        if attempt < retries:
            logger.info(f"🔄 Retrying in {delay:.1f}s...")
            time.sleep(delay)
            delay *= 2  # Exponential back-off

    logger.error(f"💀 All {retries} attempts failed for {to_email}.")
    return False

