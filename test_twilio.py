from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get Twilio credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
phone_number = os.getenv('TWILIO_PHONE_NUMBER')

print(f"Account SID: {account_sid}")
print(f"Phone Number: {phone_number}")

try:
    # Test Twilio connection
    client = Client(account_sid, auth_token)
    
    # Get account info
    account = client.api.accounts(account_sid).fetch()
    print(f"✅ Twilio connection successful!")
    print(f"Account Status: {account.status}")
    
    # Get phone number info
    incoming_phone_numbers = client.incoming_phone_numbers.list()
    print(f"✅ Phone numbers found: {len(incoming_phone_numbers)}")
    
    for number in incoming_phone_numbers:
        print(f"  📞 {number.phone_number} - {number.friendly_name}")
        print(f"     Voice URL: {number.voice_url or 'Not configured'}")
    
except Exception as e:
    print(f"❌ Twilio connection failed: {e}")