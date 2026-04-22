import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add app directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'app'))

# Load environment
load_dotenv()

from config import settings
from database import Database, get_subscribed_users, unsubscribe_user

def verify_local_mode():
    print(f"--- Verification for Local Testing Mode ---")
    print(f"USE_LOCAL_DB setting: {settings.USE_LOCAL_DB}")

    if not settings.USE_LOCAL_DB:
        print("❌ Error: USE_LOCAL_DB is not True in your .env file.")
        return

    # Simulate connection
    Database.connect()

    # Get users
    users = get_subscribed_users()
    print(f"✔ Fetched {len(users)} subscribed users from Mock Data.")
    for u in users:
        print(f"   - {u['name']} ({u['email']})")

    # Test unsubscribe
    test_email = "arjun@example.com"
    print(f"✔ Testing unsubscribe for {test_email}...")
    success = unsubscribe_user(test_email)
    if success:
        print(f"   - [MOCK] Successfully unsubscribed {test_email}.")
    
    # Verify change
    updated_users = get_subscribed_users()
    if any(u['email'] == test_email for u in updated_users):
        print(f"❌ Error: {test_email} still found in subscribed list.")
    else:
        print(f"✔ User {test_email} was removed from the list.")

if __name__ == "__main__":
    verify_local_mode()
