"""
email_sender.py - Email delivery via Gmail SMTP with retry logic
"""

import logging
import smtplib
import time
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
    Send an HTML email via Gmail SMTP with exponential back-off retry.
    Returns True on success, False after all retries fail.
    """
    attempt = 0
    delay = settings.RETRY_DELAY

    while attempt < retries:
        attempt += 1
        try:
            # Create message container
            msg = MIMEMultipart()
            msg["From"] = settings.EMAIL_FROM
            msg["To"] = to_email
            msg["Subject"] = subject
            
            # Custom headers for headers
            msg["X-Entity-Ref-ID"] = f"newsletter-{to_email}"
            msg["List-Unsubscribe"] = f"<{settings.BASE_URL}/unsubscribe?email={to_email}>"

            # Attach HTML body
            msg.attach(MIMEText(html_body, "html"))


            # Connect and send
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()  # <--- This is the magic line that fixes the freeze!
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)


            # Connect and send
            #with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
             #   server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
             #   server.send_message(msg)

            logger.info(
                f"✅ Email sent to {to_email} | Attempt: {attempt}"
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
