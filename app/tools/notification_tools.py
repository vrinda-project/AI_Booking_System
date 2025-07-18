from langchain.tools import Tool
from typing import List
from ..services.twilio_service import TwilioService

def send_sms_notification(input_str: str) -> str:
    """Send SMS notification to patient"""
    try:
        # Parse input - expecting "phone:+1234567890,message:Your appointment is confirmed"
        params = dict(item.split(':', 1) for item in input_str.split(',', 1))
        phone = params['phone']
        message = params['message']
        
        twilio_service = TwilioService()
        success = twilio_service.send_sms(phone, message)
        
        return f"SMS sent successfully: {success}"
    except Exception as e:
        return f"Error sending SMS: {str(e)}"

def create_notification_tools() -> List[Tool]:
    """Create notification tools for agents"""
    return [
        Tool(
            name="send_sms",
            description="Send SMS notification to patient. Input format: 'phone:+1234567890,message:Your appointment is confirmed'",
            func=send_sms_notification
        )
    ]