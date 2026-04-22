"""
scheduler.py - APScheduler weekly newsletter job (Sunday 9 AM)
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from config import settings

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler(timezone="Asia/Kolkata")


def _newsletter_job() -> None:
    """The actual job executed by APScheduler."""
    # Import here to avoid circular import at module load
    from service import run_newsletter_pipeline

    logger.info("⏰ Scheduler triggered: Running weekly newsletter pipeline...")
    result = run_newsletter_pipeline()
    logger.info(f"📊 Job result: {result.summary()}")


def _job_listener(event) -> None:
    """Log APScheduler job outcomes."""
    if event.exception:
        logger.error(
            f"❌ Scheduler job FAILED: {event.job_id} — {event.exception}"
        )
    else:
        logger.info(f"✅ Scheduler job completed successfully: {event.job_id}")


def start_scheduler() -> None:
    """Initialize and start the background scheduler."""
    _scheduler.add_listener(_job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    _scheduler.add_job(
        func=_newsletter_job,
        trigger=CronTrigger(
            day_of_week=settings.SCHEDULER_DAY_OF_WEEK,
            hour=settings.SCHEDULER_HOUR,
            minute=settings.SCHEDULER_MINUTE,
        ),
        id="weekly_newsletter",
        name="Weekly Newsletter Dispatch",
        replace_existing=True,
        misfire_grace_time=3600,   # 1-hour grace window if server was down
        coalesce=True,             # Don't run multiple missed jobs
    )

    _scheduler.start()
    next_run = _scheduler.get_job("weekly_newsletter").next_run_time
    logger.info(
        f"📅 Scheduler started. "
        f"Next run: {next_run.strftime('%A, %d %b %Y at %I:%M %p %Z')}"
    )


def stop_scheduler() -> None:
    """Gracefully stop the scheduler."""
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("🛑 Scheduler stopped.")


def get_scheduler_status() -> dict:
    """Return scheduler status for health check."""
    if not _scheduler.running:
        return {"running": False, "next_run": None}

    job = _scheduler.get_job("weekly_newsletter")
    next_run = job.next_run_time if job else None
    return {
        "running": True,
        "next_run": next_run.isoformat() if next_run else None,
        "job_id": "weekly_newsletter",
        "schedule": f"Every {settings.SCHEDULER_DAY_OF_WEEK.upper()} at "
                    f"{settings.SCHEDULER_HOUR:02d}:{settings.SCHEDULER_MINUTE:02d} IST",
    }
