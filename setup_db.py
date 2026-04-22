import logging
from pymongo import ASCENDING, IndexModel
from app.database import Database
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_indexes():
    """Create essential indexes for performance and uniqueness."""
    try:
        print(f"--- Setting up MongoDB Indexes for {settings.MONGODB_DB_NAME} ---")
        Database.connect()
        collection = Database.users_collection()

        # Define indexes
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True, name="unique_email"),
            IndexModel([("newsletter", ASCENDING)], name="newsletter_status"),
            IndexModel([("last_sent", ASCENDING)], name="last_sent_lookup")
        ]

        # Apply indexes
        result = collection.create_indexes(indexes)
        logger.info(f"✅ Indexes created: {result}")
        
    except Exception as e:
        logger.error(f"❌ Failed to set up indexes: {e}")
    finally:
        Database.disconnect()

if __name__ == "__main__":
    setup_indexes()
