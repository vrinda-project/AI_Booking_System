import google.generativeai as genai
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..config import settings
from .booking_service import BookingService
import json

class AIService:
    def __init__(self, db: Session):
        self.db = db
        self.booking_service = BookingService(db)
        genai.configure(api_key=settings.google_ai_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.conversations = {}
    
    def get_conversation_context(self, phone: str) -> Dict:
        if phone not in self.conversations:
            self.conversations[phone] = {
                'messages': [],
                'state': 'greeting',
                'booking_data': {}
            }
        return self.conversations[phone]
    
    def process_message(self, phone: str, message: str) -> str:
        context = self.get_conversation_context(phone)
        context['messages'].append({'role': 'user', 'content': message})
        
        # Determine intent
        intent = self._classify_intent(message)
        
        if intent == 'booking':
            response = self._handle_booking(phone, message, context)
        elif intent == 'symptoms':
            response = self._handle_symptoms(message)
        elif intent == 'general':
            response = self._handle_general_query(message)
        else:
            response = "I can help you book appointments, answer questions about symptoms, or provide general information. How can I assist you today?"
        
        context['messages'].append({'role': 'assistant', 'content': response})
        return response
    
    def _classify_intent(self, message: str) -> str:
        prompt = f"""
        Classify the following message into one of these categories:
        - booking: User wants to book, reschedule, or cancel an appointment
        - symptoms: User is describing symptoms or asking about medical conditions
        - general: General questions about hospital services, hours, etc.
        
        Message: "{message}"
        
        Respond with only the category name.
        """
        
        response = self.model.generate_content(prompt)
        return response.text.strip().lower()
    
    def _handle_booking(self, phone: str, message: str, context: Dict) -> str:
        # Extract booking information using AI
        prompt = f"""
        Extract booking information from this message: "{message}"
        
        Look for:
        - Doctor name or specialty
        - Preferred date/time
        - Department preference
        - Patient name
        
        Previous context: {json.dumps(context.get('booking_data', {}))}
        
        Return JSON with extracted information or null for missing fields:
        {{"doctor": null, "specialty": null, "date": null, "time": null, "department": null, "name": null}}
        """
        
        response = self.model.generate_content(prompt)
        try:
            booking_info = json.loads(response.text)
            context['booking_data'].update({k: v for k, v in booking_info.items() if v})
        except:
            pass
        
        # Generate appropriate response based on collected information
        if self._has_complete_booking_info(context['booking_data']):
            return self._attempt_booking(phone, context['booking_data'])
        else:
            return self._request_missing_info(context['booking_data'])
    
    def _handle_symptoms(self, message: str) -> str:
        departments = self.booking_service.get_departments()
        dept_info = [f"{d.name}: {d.description}" for d in departments]
        
        prompt = f"""
        Based on these symptoms: "{message}"
        
        Available departments:
        {chr(10).join(dept_info)}
        
        Recommend the most appropriate department and explain why.
        Also indicate urgency level (emergency, urgent, routine).
        Be helpful but remind them to consult with a doctor for proper diagnosis.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def _handle_general_query(self, message: str) -> str:
        prompt = f"""
        Answer this general hospital question: "{message}"
        
        Provide helpful information about:
        - Hospital services and departments
        - General appointment procedures
        - Contact information
        - Operating hours (assume 24/7 for emergencies, 8 AM - 6 PM for regular appointments)
        
        Keep response concise and helpful.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def _has_complete_booking_info(self, booking_data: Dict) -> bool:
        required = ['name', 'date', 'time']
        return all(booking_data.get(field) for field in required)
    
    def _request_missing_info(self, booking_data: Dict) -> str:
        missing = []
        if not booking_data.get('name'):
            missing.append('your name')
        if not booking_data.get('date'):
            missing.append('preferred date')
        if not booking_data.get('time'):
            missing.append('preferred time')
        if not booking_data.get('doctor') and not booking_data.get('department'):
            missing.append('doctor or department preference')
        
        return f"I need a few more details to book your appointment. Please provide: {', '.join(missing)}."
    
    def _attempt_booking(self, phone: str, booking_data: Dict) -> str:
        try:
            # This is a simplified booking attempt
            # In real implementation, you'd parse dates, find doctors, check availability
            return f"Great! I'm booking your appointment for {booking_data['name']} on {booking_data['date']} at {booking_data['time']}. You'll receive a confirmation SMS shortly."
        except Exception as e:
            return f"I'm sorry, there was an issue booking your appointment. Please try a different time or contact our staff directly."