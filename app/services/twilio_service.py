from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from ..config import settings

class TwilioService:
    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    
    def create_voice_response(self, message: str, gather_input: bool = True) -> str:
        response = VoiceResponse()
        
        if gather_input:
            gather = response.gather(
                input='speech',
                timeout=5,
                speech_timeout='auto',
                action='/api/twilio/voice/gather',
                method='POST'
            )
            gather.say(message, voice='alice', language='en-US')
            response.say("I didn't hear anything. Please try again.", voice='alice')
        else:
            response.say(message, voice='alice', language='en-US')
            response.hangup()
        
        return str(response)
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        try:
            self.client.messages.create(
                body=message,
                from_=settings.twilio_phone_number,
                to=to_phone
            )
            return True
        except Exception as e:
            print(f"SMS sending failed: {e}")
            return False