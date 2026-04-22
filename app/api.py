"""
api.py - FastAPI router: health check, unsubscribe, send-test
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request, Depends, Header
from fastapi.security import APIKeyHeader
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings
from app.database import unsubscribe_user
from app.scheduler import get_scheduler_status
from app.dashboard_template import get_dashboard_html

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# API Key security scheme
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def validate_api_key(api_key: str = Depends(api_key_header)):
    """Check if the provided API key matches the configured ADMIN_API_KEY."""
    if not api_key or api_key != settings.ADMIN_API_KEY:
        logger.warning(f"🔒 Unauthorized access attempt blocked.")
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Invalid or missing API Key"
        )
    return api_key


# ─── Request / Response models ────────────────────────────────────────────────

class TestNewsletterRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = "Test Student"
    interests: Optional[list[str]] = ["Computer Science", "AI"]
    marks: Optional[int] = 75
    budget: Optional[int] = 200000
    location: Optional[str] = "Delhi"

class SubscriptionRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = "Student"
    interests: Optional[list[str]] = []
    marks: Optional[int] = None
    budget: Optional[int] = None
    location: Optional[str] = None


# ─── GET /health ─────────────────────────────────────────────────────────────

@router.get("/health", tags=["System"])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def health_check(request: Request):
    """
    Returns service status including Postgres connectivity and scheduler state.
    """
    from app.database import Database, get_subscribed_users

    # Quick DB connectivity check
    db_status = "connected"
    if settings.USE_LOCAL_DB:
        db_status = "local_mock"
    else:
        try:
            # Simple query to check connection
            get_subscribed_users()
        except Exception as e:
            db_status = f"error: {str(e)}"
            logger.error(f"❌ DB health check failed: {e}")

    scheduler = get_scheduler_status()

    return {
        "status": "ok",
        "service": "R.S Education Solution Newsletter Service",
        "database": db_status,
        "scheduler": scheduler,
        "version": "1.0.0",
    }


# ─── GET /dashboard (UI) ──────────────────────────────────────────────────────

@router.get("/dashboard", tags=["System"], response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Return the premium claymorphism testing dashboard.
    """
    return HTMLResponse(content=get_dashboard_html(admin_key=settings.ADMIN_API_KEY))


# ─── GET /unsubscribe ─────────────────────────────────────────────────────────

@router.get("/unsubscribe", tags=["Subscription"], response_class=HTMLResponse)
@limiter.limit("20/minute")
async def unsubscribe(
    request: Request,
    email: str = Query(..., description="Email address to unsubscribe"),
):
    """
    Unsubscribe a user from the newsletter.
    PERMANENTLY DELETES the user from the PostgreSQL database.
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
            message="You have been successfully unsubscribed from R.S Education Solution newsletters.",
        )
    )


# ─── POST /subscribe ──────────────────────────────────────────────────────────

@router.post("/subscribe", tags=["Subscription"])
@limiter.limit("10/minute")
async def subscribe(request: Request, body: SubscriptionRequest):
    """
    Endpoint for the main website to subscribe a new student.
    Data is saved to the PostgreSQL database.
    """
    from app.database import add_user

    logger.info(f"✨ New subscription request: {body.email}")

    success = add_user(body.model_dump())

    if not success:
        raise HTTPException(
            status_code=500, 
            detail="We couldn't save your subscription. Please try again later."
        )

    return {
        "status": "success",
        "message": f"Welcome! {body.email} has been subscribed to R.S Education Solution updates.",
    }


# ─── GET /users (Admin) ───────────────────────────────────────────────────────

@router.get("/users", tags=["Admin"], dependencies=[Depends(validate_api_key)])
@limiter.limit("5/minute")
async def list_users(request: Request):
    """
    Returns the list of all subscribed users from the database.
    Requires ADMIN_API_KEY.
    """
    from app.database import get_subscribed_users
    
    try:
        users = get_subscribed_users()
        return {
            "status": "success",
            "count": len(users),
            "users": users
        }
    except Exception as e:
        logger.error(f"❌ Failed to fetch user list: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch user list.")


# ─── POST /send-test ──────────────────────────────────────────────────────────

@router.post("/send-test", tags=["Debug"], dependencies=[Depends(validate_api_key)])
@limiter.limit("5/minute")
async def send_test(request: Request, body: TestNewsletterRequest):
    """
    Send a test newsletter to a specific email.
    Useful for debugging templates and AI generation.
    Does NOT affect the database or last_sent timestamps.
    """
    from app.service import send_test_newsletter

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

@router.post("/trigger-now", tags=["Admin"], dependencies=[Depends(validate_api_key)])
@limiter.limit("2/minute")
async def trigger_now(request: Request):
    """
    Manually trigger the newsletter pipeline immediately.
    Useful for testing the full pipeline end-to-end.
    """
    from app.service import run_newsletter_pipeline

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
  <title>{title} — R.S Education Solution</title>
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
    <div class="footer">© 2025 R.S Education Solution. All rights reserved.</div>
  </div>
</body>
</html>"""
