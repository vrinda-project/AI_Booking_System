from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..services import TwilioService, AIService

router = APIRouter(prefix="/api/twilio", tags=["twilio"])

@router.post("/voice/incoming")
async def handle_incoming_call(request: Request, db: Session = Depends(get_db)):
    """MANDATORY: Handle incoming voice calls using LangChain agents"""
    twilio_service = TwilioService()
    
    # Welcome message
    welcome_message = """
    Hello! Welcome to City Hospital's AI appointment booking system powered by advanced AI agents. 
    I can help you book appointments, cancel or reschedule existing appointments, 
    analyze symptoms for department recommendations, or answer general questions. 
    How can I assist you today?
    """
    
    twiml_response = twilio_service.create_voice_response(welcome_message)
    return Response(content=twiml_response, media_type="application/xml")

@router.post("/voice/gather")
async def handle_voice_input(
    request: Request,
    SpeechResult: str = Form(None),
    From: str = Form(...),
    db: Session = Depends(get_db)
):
    """MANDATORY: Process speech input through LangChain agent hierarchy"""
    twilio_service = TwilioService()
    # REQUIRED: Use LangChain agent-based AI service
    ai_service = AIService(db)
    
    if not SpeechResult:
        twiml_response = twilio_service.create_voice_response(
            "I didn't catch that. Could you please repeat?"
        )
        return Response(content=twiml_response, media_type="application/xml")
    
    # MANDATORY: Process through LangChain agent system
    ai_response = ai_service.process_message(From, SpeechResult)
    
    # Check if this should end the conversation
    end_conversation = any(phrase in ai_response.lower() for phrase in [
        "goodbye", "thank you for calling", "appointment confirmed", "appointment cancelled", "appointment rescheduled"
    ])
    
    twiml_response = twilio_service.create_voice_response(
        ai_response, 
        gather_input=not end_conversation
    )
    
    return Response(content=twiml_response, media_type="application/xml")

@router.post("/sms/send")
async def send_confirmation_sms(
    phone: str,
    message: str,
    db: Session = Depends(get_db)
):
    """Send SMS confirmation"""
    twilio_service = TwilioService()
    success = twilio_service.send_sms(phone, message)
    return {"success": success}