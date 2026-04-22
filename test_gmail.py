import os
import sys
from dotenv import load_dotenv

# Add app directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'app'))

# Load environment
load_dotenv()

from config import settings
from email_sender import send_email

def test_gmail_delivery():
    print(f"--- Verification for Gmail SMTP Delivery ---")
    print(f"SMTP User: {settings.SMTP_USER}")
    print(f"Sending test email to: {settings.SMTP_USER}")

    # Test send_email
    success = send_email(
        to_email=settings.SMTP_USER,
        to_name="Test User",
        subject="🚀 R.S Education - SMTP Test",
        html_body="""
        <h1>SMTP Test Successful!</h1>
        <p>This email was sent using Gmail SMTP from your Newsletter Service.</p>
        <p><b>Check your inbox!</b></p>
        """
    )
    
    if success:
        print("✔ SMTP test email sent successfully!")
    else:
        print("❌ SMTP test email failed. Check your App Password or internet connection.")

if __name__ == "__main__":
    test_gmail_delivery()
