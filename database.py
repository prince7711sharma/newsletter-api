"""
database.py - MongoDB connection and user operations
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, PyMongoError

from config import settings

logger = logging.getLogger(__name__)


class Database:
    _client: Optional[MongoClient] = None
    _db = None

    @classmethod
    def connect(cls) -> None:
        """Establish MongoDB connection."""
        try:
            cls._client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
            )
            # Ping to verify connection
            cls._client.admin.command("ping")
            cls._db = cls._client[settings.MONGODB_DB_NAME]
            logger.info("✅ MongoDB connected successfully.")
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise

    @classmethod
    def disconnect(cls) -> None:
        """Close MongoDB connection."""
        if cls._client:
            cls._client.close()
            logger.info("🔌 MongoDB disconnected.")

    @classmethod
    def get_collection(cls, name: str) -> Collection:
        if cls._db is None:
            raise RuntimeError("Database not connected. Call Database.connect() first.")
        return cls._db[name]

    @classmethod
    def users_collection(cls) -> Collection:
        return cls.get_collection(settings.USERS_COLLECTION)


def get_subscribed_users() -> list[dict]:
    """
    Fetch all users with newsletter=True.
    Filters out users already sent a newsletter this week.
    """
    try:
        collection = Database.users_collection()
        users = list(
            collection.find(
                {"newsletter": True},
                {
                    "_id": 1,
                    "name": 1,
                    "email": 1,
                    "interests": 1,
                    "marks": 1,
                    "budget": 1,
                    "location": 1,
                    "last_sent": 1,
                },
            )
        )
        logger.info(f"📋 Found {len(users)} subscribed users.")
        return users
    except PyMongoError as e:
        logger.error(f"❌ Error fetching users: {e}")
        return []


def unsubscribe_user(email: str) -> bool:
    """Set newsletter=False for the given email."""
    try:
        collection = Database.users_collection()
        result = collection.update_one(
            {"email": email},
            {"$set": {"newsletter": False}},
        )
        if result.matched_count == 0:
            logger.warning(f"⚠️ No user found with email: {email}")
            return False
        logger.info(f"✅ Unsubscribed: {email}")
        return True
    except PyMongoError as e:
        logger.error(f"❌ Error unsubscribing {email}: {e}")
        return False


def update_last_sent(email: str) -> None:
    """Update last_sent timestamp after successful email delivery."""
    try:
        collection = Database.users_collection()
        collection.update_one(
            {"email": email},
            {"$set": {"last_sent": datetime.now(timezone.utc)}},
        )
    except PyMongoError as e:
        logger.error(f"❌ Could not update last_sent for {email}: {e}")


def was_sent_this_week(user: dict) -> bool:
    """Return True if newsletter was already sent within the last 7 days."""
    last_sent = user.get("last_sent")
    if not last_sent:
        return False
    if last_sent.tzinfo is None:
        last_sent = last_sent.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - last_sent
    return delta.days < 7
