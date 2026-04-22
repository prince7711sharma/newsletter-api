import os
import sys
from dotenv import load_dotenv

# Add app directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'app'))

# Load environment
load_dotenv()

from config import settings
from database import Database, get_subscribed_users, add_user, unsubscribe_user

def verify_postgres_logic():
    print(f"--- Verification for PostgreSQL & Subscriptions ---")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    print(f"USE_LOCAL_DB: {settings.USE_LOCAL_DB}")

    # Simulating connection (mock or real)
    Database.connect()

    # 1. Test Subscription (Add User)
    new_user = {
        "name": "Test Student",
        "email": "test@rseducation.com",
        "interests": ["Physics", "Space"],
        "marks": 80,
        "budget": 400000,
        "location": "Chennai"
    }
    print(f"✔ Testing subscription for {new_user['email']}...")
    add_user(new_user)

    # 2. Test Fetching
    users = get_subscribed_users()
    print(f"✔ Fetched {len(users)} users from database.")
    
    # 3. Test Deletion (Unsubscribe)
    print(f"✔ Testing unsubscription (DELETION) for {new_user['email']}...")
    success = unsubscribe_user(new_user['email'])
    if success:
        print(f"   - Successfully DELETED user from database.")
    
    # 4. Final check
    final_users = get_subscribed_users()
    if any(u['email'] == new_user['email'] for u in final_users):
        print(f"❌ Error: User still exists in database.")
    else:
        print(f"✔ Final check: User record is gone. Automation for this email is stopped.")

if __name__ == "__main__":
    verify_postgres_logic()
