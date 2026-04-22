"""
service.py - Core business logic for the newsletter pipeline
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from app.ai_generator import generate_newsletter_content
from app.database import get_subscribed_users, update_last_sent, was_sent_this_week
from app.email_builder import build_html_email, get_email_subject
from app.email_sender import send_email
from app.config import settings

logger = logging.getLogger(__name__)


# ─── Result tracking ──────────────────────────────────────────────────────────

@dataclass
class NewsletterResult:
    total: int = 0
    sent: int = 0
    skipped: int = 0
    failed: int = 0
    failed_emails: list[str] = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "total_subscribers": self.total,
            "sent": self.sent,
            "skipped_already_sent": self.skipped,
            "failed": self.failed,
            "failed_emails": self.failed_emails,
        }


# ─── Main pipeline ────────────────────────────────────────────────────────────

def run_newsletter_pipeline() -> NewsletterResult:
    """
    Full weekly newsletter pipeline:
    1. Fetch subscribed users
    2. Filter already-sent-this-week
    3. Generate AI content
    4. Build HTML email
    5. Send email
    6. Update last_sent
    Processes in batches to avoid rate limits.
    """
    result = NewsletterResult()

    logger.info("🚀 Starting newsletter pipeline...")
    users = get_subscribed_users()
    result.total = len(users)

    if not users:
        logger.info("📭 No subscribed users found. Pipeline complete.")
        return result

    # Filter users who already received this week's newsletter
    pending_users = []
    for user in users:
        if was_sent_this_week(user):
            logger.info(f"⏭️  Skipping {user.get('email')} — already sent this week.")
            result.skipped += 1
        else:
            pending_users.append(user)

    logger.info(
        f"📬 {len(pending_users)} users to process "
        f"({result.skipped} skipped)."
    )

    # Process in batches
    for batch_start in range(0, len(pending_users), settings.EMAIL_BATCH_SIZE):
        batch = pending_users[batch_start: batch_start + settings.EMAIL_BATCH_SIZE]
        logger.info(
            f"📦 Processing batch "
            f"{batch_start // settings.EMAIL_BATCH_SIZE + 1} "
            f"({len(batch)} users)..."
        )

        for user in batch:
            _process_single_user(user, result)

        # Delay between batches (rate limit protection)
        if batch_start + settings.EMAIL_BATCH_SIZE < len(pending_users):
            logger.info(
                f"⏳ Batch complete. Waiting "
                f"{settings.EMAIL_BATCH_DELAY}s before next batch..."
            )
            time.sleep(settings.EMAIL_BATCH_DELAY)

    logger.info(
        f"✅ Pipeline complete. "
        f"Sent: {result.sent} | "
        f"Skipped: {result.skipped} | "
        f"Failed: {result.failed}"
    )
    return result


def _process_single_user(user: dict, result: NewsletterResult) -> None:
    """Generate and send newsletter for a single user."""
    email = user.get("email", "")
    name = user.get("name", "Student")

    if not email:
        logger.warning("⚠️ User without email found, skipping.")
        result.skipped += 1
        return

    try:
        # 1. Generate AI content
        content = generate_newsletter_content(user)

        # 2. Build HTML email
        html = build_html_email(name, content, email)
        subject = get_email_subject(name)

        # 3. Send email
        success = send_email(
            to_email=email,
            to_name=name,
            subject=subject,
            html_body=html,
        )

        if success:
            # 4. Update last_sent in DB
            update_last_sent(email)
            result.sent += 1
        else:
            result.failed += 1
            result.failed_emails.append(email)

    except Exception as e:
        logger.error(f"❌ Unexpected error for {email}: {e}")
        result.failed += 1
        result.failed_emails.append(email)


# ─── Test send (single user) ─────────────────────────────────────────────────

def send_test_newsletter(
    test_email: str,
    name: str = "Test Student",
    interests: Optional[list] = None,
    marks: int = 75,
    budget: int = 200000,
    location: str = "Delhi",
) -> dict:
    """
    Send a one-off test newsletter to verify the pipeline.
    Does NOT update last_sent or affect real user data.
    """
    user = {
        "name": name,
        "email": test_email,
        "interests": interests or ["Computer Science", "AI"],
        "marks": marks,
        "budget": budget,
        "location": location,
    }

    logger.info(f"🧪 Sending test newsletter to {test_email}...")

    content = generate_newsletter_content(user)
    html = build_html_email(name, content, test_email)
    subject = get_email_subject(name)

    success = send_email(
        to_email=test_email,
        to_name=name,
        subject=subject,
        html_body=html,
    )

    return {
        "success": success,
        "email": test_email,
        "subject": subject,
        "message": "Test email sent successfully!" if success else "Failed to send test email.",
    }
