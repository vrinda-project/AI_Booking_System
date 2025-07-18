from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
from ..tools.database_tools import create_booking_tools
from ..tools.notification_tools import create_notification_tools
from ..config import settings

class CancelAgent:
    """MANDATORY LangChain Agent for appointment cancellation"""
    
    def __init__(self):
        # REQUIRED: Use ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.google_ai_api_key,
            temperature=0.1
        )
        
        # REQUIRED: Define LangChain tools
        self.tools = self._create_tools()
        
        # REQUIRED: Create LangChain agent with prompt template
        self.prompt = self._create_prompt()
        
        # MANDATORY: Use create_openai_functions_agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # REQUIRED: AgentExecutor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for cancel agent"""
        # Add cancellation-specific tool
        cancel_tool = Tool(
            name="cancel_appointment",
            description="Cancel an appointment by appointment ID. Input: appointment_id",
            func=self._cancel_appointment_db
        )
        
        booking_tools = create_booking_tools()
        notification_tools = create_notification_tools()
        
        return [cancel_tool] + booking_tools + notification_tools
    
    def _cancel_appointment_db(self, appointment_id: str) -> str:
        """Cancel appointment in database"""
        try:
            from ..database import SessionLocal
            from ..models import Appointment, TimeSlot
            
            db = SessionLocal()
            appointment = db.query(Appointment).filter(Appointment.id == int(appointment_id)).first()
            
            if not appointment:
                db.close()
                return "Appointment not found"
            
            # Update appointment status
            appointment.status = "cancelled"
            
            # Make time slot available again
            slot = db.query(TimeSlot).filter(
                TimeSlot.doctor_id == appointment.doctor_id,
                TimeSlot.start_time <= appointment.appointment_datetime,
                TimeSlot.end_time > appointment.appointment_datetime
            ).first()
            
            if slot:
                slot.is_available = True
            
            db.commit()
            db.close()
            
            return f"Appointment {appointment_id} cancelled successfully"
        except Exception as e:
            return f"Error cancelling appointment: {str(e)}"
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create prompt template for cancel agent"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are a hospital appointment cancellation agent. Your role is to help patients cancel their appointments professionally and efficiently.

CANCELLATION PROCESS:
1. Identify the patient and their appointment
2. Verify appointment details
3. Cancel the appointment in the system
4. Send cancellation confirmation to patient
5. Inform about cancellation policy if applicable

AVAILABLE TOOLS:
- get_patient_history: Get patient's appointments
- cancel_appointment: Cancel specific appointment
- send_sms: Send cancellation confirmation

IMPORTANT RULES:
- Verify patient identity before cancelling
- Explain cancellation policy (24-hour notice preferred)
- Send confirmation of cancellation
- Be empathetic and professional
- Offer to reschedule if appropriate

Current conversation context: {context}"""),
            ("user", "{input}"),
            ("assistant", "{agent_scratchpad}")
        ])
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process cancellation request through LangChain agent"""
        try:
            result = self.executor.invoke(input_data)
            return {
                "success": True,
                "response": result.get("output", ""),
                "agent_type": "cancel"
            }
        except Exception as e:
            return {
                "success": False,
                "response": f"Cancel agent error: {str(e)}",
                "agent_type": "cancel"
            }