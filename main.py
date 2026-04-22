"""
main.py - FastAPI application entry point
"""

import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from api import router, limiter
from config import settings
from database import Database
from scheduler import start_scheduler, stop_scheduler

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
    start_scheduler()
    logger.info("✅ Service ready.")
    yield
    # ── Shutdown ──
    logger.info("🛑 Shutting down Newsletter Service...")
    stop_scheduler()
    Database.disconnect()
    logger.info("👋 Service stopped cleanly.")


# ─── App factory ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="R.S Education — Newsletter Service",
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

# CORS (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)


# ─── Root ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "R.S Education Newsletter Service",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=False,
        log_level="info",
    )
