"""
main.py - FastAPI application entry point
"""

import logging
import sys
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Imports from app package
from app.api import router, limiter
from app.config import settings
from app.database import Database
from app.scheduler import start_scheduler, stop_scheduler

# ─── Logging setup ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("newsletter_service.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


# ─── Lifespan (startup / shutdown) ────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    logger.info("🌟 R.S Education Newsletter Service starting up...")
    Database.connect()
    # start_scheduler()  # Disabled: User wants manual trigger only
    logger.info("✅ Service ready. (Manual Trigger Mode)")
    yield
    # ── Shutdown ──
    logger.info("🛑 Shutting down Newsletter Service...")
    # stop_scheduler()
    Database.disconnect()
    logger.info("👋 Service stopped cleanly.")


# ─── App factory ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="R.S Education Solution — Newsletter Service",
    description=(
        "Automated AI-powered weekly newsletter system for student counselling. "
        "Generates personalized college, scholarship, and career content using Groq AI."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS (restrict to your website domain in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace ["*"] with ["https://yourdomain.com"] in prod
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)


# ─── Root ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"], response_class=HTMLResponse)
async def root(request: Request):
    from app.dashboard_template import get_dashboard_html
    from app.config import settings
    return HTMLResponse(content=get_dashboard_html(admin_key=settings.ADMIN_API_KEY))


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=False,
        log_level="info",
    )
