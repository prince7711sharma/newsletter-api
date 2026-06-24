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
            # If RESEND_API_KEY is configured, send email via Resend HTTP API (HTTPS port 443)
            # This avoids Render Free tier SMTP blocking.
            if settings.RESEND_API_KEY:
                logger.info(f"📤 Attempting to send email to {to_email} via Resend API...")
                
                from_email = settings.EMAIL_FROM
                if settings.EMAIL_FROM_NAME and "<" not in from_email:
                    from_email = f"{settings.EMAIL_FROM_NAME} <{from_email}>"
                
                headers = {
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "from": from_email,
                    "to": [to_email],
                    "subject": subject,
                    "html": html_body,
                    "headers": {
                        "X-Entity-Ref-ID": f"newsletter-{to_email}",
                        "List-Unsubscribe": f"<{settings.BASE_URL}/unsubscribe?email={to_email}>"
                    }
                }
                
                with httpx.Client(timeout=15.0) as client:
                    response = client.post(
                        "https://api.resend.com/emails",
                        json=payload,
                        headers=headers,
                    )
                
                if response.status_code in (200, 201):
                    logger.info(f"✅ Email sent via Resend to {to_email} | Attempt: {attempt}")
                    return True
                else:
                    error_msg = f"Resend API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            
            else:
                logger.info(f"📤 Attempting to send email to {to_email} via SMTP...")
                # Create message container
                msg = MIMEMultipart()
                msg["From"] = settings.EMAIL_FROM
                msg["To"] = to_email
                msg["Subject"] = subject
                
                # Custom headers
                msg["X-Entity-Ref-ID"] = f"newsletter-{to_email}"
                msg["List-Unsubscribe"] = f"<{settings.BASE_URL}/unsubscribe?email={to_email}>"

                # Attach HTML body
                msg.attach(MIMEText(html_body, "html"))

                # Connect and send dynamically based on the port configured
                if settings.SMTP_PORT == 465:
                    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                        server.send_message(msg)
                else:
                    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                        try:
                            server.starttls()
                        except smtplib.SMTPException:
                            pass
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                        server.send_message(msg)

                logger.info(
                    f"✅ Email sent to {to_email} via SMTP | Attempt: {attempt}"
                )
                return True

        except smtplib.SMTPException as e:
            logger.warning(
                f"⚠️ SMTP error for {to_email} "
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

