"""
api.py - FastAPI router: health check, unsubscribe, send-test
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from config import settings
from database import unsubscribe_user
from scheduler import get_scheduler_status

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


# ─── Request / Response models ────────────────────────────────────────────────

class TestNewsletterRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = "Test Student"
    interests: Optional[list[str]] = ["Computer Science", "AI"]
    marks: Optional[int] = 75
    budget: Optional[int] = 200000
    location: Optional[str] = "Delhi"


# ─── GET /health ─────────────────────────────────────────────────────────────

@router.get("/health", tags=["System"])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def health_check(request: Request):
    """
    Returns service status including DB connectivity and scheduler state.
    """
    from database import Database

    # Quick DB connectivity check
    db_status = "connected"
    try:
        Database.users_collection().find_one({}, {"_id": 1})
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"❌ DB health check failed: {e}")

    scheduler = get_scheduler_status()

    return {
        "status": "ok",
        "service": "R.S Education Newsletter Service",
        "database": db_status,
        "scheduler": scheduler,
        "version": "1.0.0",
    }


# ─── GET /unsubscribe ─────────────────────────────────────────────────────────

@router.get("/unsubscribe", tags=["Subscription"], response_class=HTMLResponse)
@limiter.limit("20/minute")
async def unsubscribe(
    request: Request,
    email: str = Query(..., description="Email address to unsubscribe"),
):
    """
    Unsubscribe a user from the newsletter.
    Sets newsletter=False in MongoDB.
    Returns a friendly HTML confirmation page.
    """
    success = unsubscribe_user(email)

    if not success:
        return HTMLResponse(
            content=_unsubscribe_page(
                email=email,
                success=False,
                message="We couldn't find that email address in our system.",
            ),
            status_code=404,
        )

    logger.info(f"👋 User unsubscribed: {email}")
    return HTMLResponse(
        content=_unsubscribe_page(
            email=email,
            success=True,
            message="You have been successfully unsubscribed from R.S Education newsletters.",
        )
    )


# ─── POST /send-test ──────────────────────────────────────────────────────────

@router.post("/send-test", tags=["Debug"])
@limiter.limit("5/minute")
async def send_test(request: Request, body: TestNewsletterRequest):
    """
    Send a test newsletter to a specific email.
    Useful for debugging templates and AI generation.
    Does NOT affect the database or last_sent timestamps.
    """
    from service import send_test_newsletter

    logger.info(f"🧪 Test send requested for: {body.email}")

    result = send_test_newsletter(
        test_email=body.email,
        name=body.name,
        interests=body.interests,
        marks=body.marks,
        budget=body.budget,
        location=body.location,
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result


# ─── POST /trigger-now  (manual trigger for admins) ──────────────────────────

@router.post("/trigger-now", tags=["Admin"])
@limiter.limit("2/minute")
async def trigger_now(request: Request):
    """
    Manually trigger the newsletter pipeline immediately.
    Useful for testing the full pipeline end-to-end.
    """
    from service import run_newsletter_pipeline

    logger.info("🔧 Manual pipeline trigger via API.")

    try:
        result = run_newsletter_pipeline()
        return {
            "status": "completed",
            "summary": result.summary(),
        }
    except Exception as e:
        logger.error(f"❌ Manual trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── HTML unsubscribe confirmation page ──────────────────────────────────────

def _unsubscribe_page(email: str, success: bool, message: str) -> str:
    icon = "✅" if success else "❌"
    color = "#1a73e8" if success else "#e53935"
    title = "Unsubscribed" if success else "Not Found"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>{title} — R.S Education</title>
  <style>
    body {{font-family:'Segoe UI',Arial,sans-serif;background:#f4f6f9;
           display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;}}
    .card {{background:#fff;border-radius:12px;padding:48px 40px;text-align:center;
            box-shadow:0 4px 24px rgba(0,0,0,0.09);max-width:460px;width:90%;}}
    .icon {{font-size:52px;margin-bottom:16px;}}
    h1 {{color:{color};font-size:24px;margin:0 0 12px;}}
    p {{color:#546e7a;font-size:14px;line-height:1.7;margin:0 0 8px;}}
    .email {{color:#1a73e8;font-weight:600;}}
    .footer {{margin-top:28px;color:#b0bec5;font-size:12px;}}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">{icon}</div>
    <h1>{title}</h1>
    <p>{message}</p>
    <p class="email">{email}</p>
    <div class="footer">© 2025 R.S Education. All rights reserved.</div>
  </div>
</body>
</html>"""
