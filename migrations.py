import logging
from app.database import Base, Database, settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Create all tables in the PostgreSQL database."""
    if settings.USE_LOCAL_DB:
        print("🧪 Running in Mock Mode. Skipping migrations.")
        return

    print(f"--- Running PostgreSQL Migrations for {settings.DATABASE_URL} ---")
    try:
        Database.connect()
        # Create all tables defined in Base (declarative_base)
        Base.metadata.create_all(Database._engine)
        logger.info("✅ Database tables created successfully.")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
    finally:
        Database.disconnect()

if __name__ == "__main__":
    run_migrations()
