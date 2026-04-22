"""
database.py - PostgreSQL connection and user operations via SQLAlchemy
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    newsletter = Column(Boolean, default=True)
    interests = Column(JSON, default=[])
    marks = Column(Integer, nullable=True)
    budget = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    last_sent = Column(DateTime(timezone=True), nullable=True)

    def to_dict(self):
        """Convert a User object to a dictionary for pipeline compatibility."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "interests": self.interests,
            "marks": self.marks,
            "budget": self.budget,
            "location": self.location,
            "last_sent": self.last_sent,
        }


# --- Mock Data for Local Testing ---
MOCK_USERS_DATA = [
    {
        "name": "Arjun Sharma",
        "email": "arjun@example.com",
        "newsletter": True,
        "interests": ["Computer Science", "Artificial Intelligence"],
        "marks": 85,
        "budget": 500000,
        "location": "Delhi",
        "last_sent": None
    },
    {
        "name": "Priya Patel",
        "email": "priya@example.com",
        "newsletter": True,
        "interests": ["Medicine", "Biology"],
        "marks": 92,
        "budget": 800000,
        "location": "Mumbai",
        "last_sent": datetime(2024, 3, 1, tzinfo=timezone.utc)
    }
]


class Database:
    _engine = None
    _SessionLocal = None

    @classmethod
    def connect(cls) -> None:
        """Initialize PostgreSQL connection using SQLAlchemy."""
        if settings.USE_LOCAL_DB:
            logger.info("🧪 Local Mock Database enabled. Skipping PostgreSQL connection.")
            return

        try:
            cls._engine = create_engine(settings.DATABASE_URL)
            cls._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls._engine)
            
            # Auto-create tables on startup (no shell needed)
            Base.metadata.create_all(cls._engine)
            
            # Simple connectivity check
            with cls._engine.connect() as conn:
                logger.info("✅ PostgreSQL connected and tables synchronized.")
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            raise

    @classmethod
    def disconnect(cls) -> None:
        if cls._engine:
            cls._engine.dispose()
            logger.info("🔌 PostgreSQL disconnected.")

    @classmethod
    def get_session(cls) -> Session:
        if settings.USE_LOCAL_DB:
            return None
        if cls._SessionLocal is None:
            raise RuntimeError("Database not connected. Call Database.connect() first.")
        return cls._SessionLocal()


def get_subscribed_users() -> List[dict]:
    """Fetch users with newsletter=True from Postgres or Local Mock."""
    if settings.USE_LOCAL_DB:
        logger.info(f"🧪 Fetching users from Mock Data (Total: {len(MOCK_USERS_DATA)})")
        return MOCK_USERS_DATA

    session = Database.get_session()
    try:
        users = session.query(User).filter(User.newsletter == True).all()
        logger.info(f"📋 Found {len(users)} subscribed users.")
        return [u.to_dict() for u in users]
    except Exception as e:
        logger.error(f"❌ Error fetching users: {e}")
        return []
    finally:
        session.close()


def unsubscribe_user(email: str) -> bool:
    """Permanently DELETE the user from the database in Postgres."""
    if settings.USE_LOCAL_DB:
        global MOCK_USERS_DATA
        new_list = [u for u in MOCK_USERS_DATA if u["email"] != email]
        if len(new_list) < len(MOCK_USERS_DATA):
            MOCK_USERS_DATA = new_list
            logger.info(f"🧪 [MOCK] Deleted user: {email}")
            return True
        return False

    session = Database.get_session()
    try:
        user = session.query(User).filter(User.email == email).first()
        if user:
            session.delete(user)
            session.commit()
            logger.info(f"✅ User deleted from Database: {email} (Unsubscribed)")
            return True
        logger.warning(f"⚠️ No user found with email: {email}")
        return False
    except Exception as e:
        logger.error(f"❌ Error deleting {email}: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def add_user(data: dict) -> bool:
    """Add a new student to the newsletter list."""
    email = data.get("email")
    if settings.USE_LOCAL_DB:
        # Check if already exists to prevent duplicates in mock list
        if any(u['email'] == email for u in MOCK_USERS_DATA):
            logger.info(f"🧪 [MOCK] User already exists: {email}")
            return True
        MOCK_USERS_DATA.append(data)
        logger.info(f"🧪 [MOCK] Added user: {email}")
        return True

    session = Database.get_session()
    try:
        # Check if user already exists
        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            logger.info(f"ℹ️ User already subscribed: {email}")
            return True

        user = User(
            name=data.get("name"),
            email=email,
            interests=data.get("interests", []),
            marks=data.get("marks"),
            budget=data.get("budget"),
            location=data.get("location")
        )
        session.add(user)
        session.commit()
        logger.info(f"✅ New user subscribed: {email}")
        return True
    except Exception as e:
        logger.error(f"❌ Error adding student {email}: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def update_last_sent(email: str) -> None:
    """Update last_sent timestamp for the record."""
    if settings.USE_LOCAL_DB:
        for u in MOCK_USERS_DATA:
            if u["email"] == email:
                u["last_sent"] = datetime.now(timezone.utc)
        return

    session = Database.get_session()
    try:
        user = session.query(User).filter(User.email == email).first()
        if user:
            user.last_sent = datetime.now(timezone.utc)
            session.commit()
    except Exception as e:
        logger.error(f"❌ Could not update last_sent for {email}: {e}")
        session.rollback()
    finally:
        session.close()


def was_sent_this_week(user: dict) -> bool:
    """Return True if newsletter was already sent within the last 7 days."""
    last_sent = user.get("last_sent")
    if not last_sent:
        return False
    if last_sent.tzinfo is None:
        last_sent = last_sent.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - last_sent
    return delta.days < 7
