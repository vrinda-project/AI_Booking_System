from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
from ..tools.database_tools import create_booking_tools
from ..tools.notification_tools import create_notification_tools
from ..tools.calendar_tools import create_calendar_tools
from ..config import settings

class RescheduleAgent:
    """MANDATORY LangChain Agent for appointment rescheduling"""
    
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
        """Create tools for reschedule agent"""
        # Add rescheduling-specific tool
        reschedule_tool = Tool(
            name="reschedule_appointment",
            description="Reschedule an appointment. Input format: 'appointment_id:1,new_datetime:2024-01-15T14:00'",
            func=self._reschedule_appointment_db
        )
        
        booking_tools = create_booking_tools()
        notification_tools = create_notification_tools()
        calendar_tools = create_calendar_tools()
        
        return [reschedule_tool] + booking_tools + notification_tools + calendar_tools
    
    def _reschedule_appointment_db(self, input_str: str) -> str:
        """Reschedule appointment in database"""
        try:
            from ..database import SessionLocal
            from ..models import Appointment, TimeSlot
            from datetime import datetime
            
            # Parse input
            params = dict(item.split(':', 1) for item in input_str.split(','))
            appointment_id = int(params['appointment_id'])
            new_datetime = datetime.fromisoformat(params['new_datetime'])
            
            db = SessionLocal()
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            
            if not appointment:
                db.close()
                return "Appointment not found"
            
            # Check if new slot is available
            new_slot = db.query(TimeSlot).filter(
                TimeSlot.doctor_id == appointment.doctor_id,
                TimeSlot.start_time <= new_datetime,
                TimeSlot.end_time > new_datetime,
                TimeSlot.is_available == True
            ).first()
            
            if not new_slot:
                db.close()
                return "New time slot is not available"
            
            # Free up old slot
            old_slot = db.query(TimeSlot).filter(
                TimeSlot.doctor_id == appointment.doctor_id,
                TimeSlot.start_time <= appointment.appointment_datetime,
                TimeSlot.end_time > appointment.appointment_datetime
            ).first()
            
            if old_slot:
                old_slot.is_available = True
            
            # Update appointment
            appointment.appointment_datetime = new_datetime
            appointment.status = "rescheduled"
            
            # Mark new slot as unavailable
            new_slot.is_available = False
            
            db.commit()
            db.close()
            
            return f"Appointment {appointment_id} rescheduled successfully to {new_datetime}"
        except Exception as e:
            return f"Error rescheduling appointment: {str(e)}"
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create prompt template for reschedule agent"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are a hospital appointment rescheduling agent. Your role is to help patients reschedule their appointments efficiently.

RESCHEDULING PROCESS:
1. Identify the patient and their current appointment
2. Understand their new preferred date/time
3. Check availability for the new time slot
4. Reschedule the appointment in the system
5. Send confirmation of the new appointment time

AVAILABLE TOOLS:
- get_patient_history: Get patient's current appointments
- check_doctor_availability: Check if new time is available
- get_time_slots: Get available time slots for doctor
- reschedule_appointment: Reschedule the appointment
- send_sms: Send reschedule confirmation

IMPORTANT RULES:
- Verify patient identity and current appointment
- Check availability before confirming reschedule
- Maximum 2 reschedules allowed per appointment
- Send confirmation with new appointment details
- Be helpful and accommodating

Current conversation context: {context}"""),
            ("user", "{input}"),
            ("assistant", "{agent_scratchpad}")
        ])
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process reschedule request through LangChain agent"""
        try:
            result = self.executor.invoke(input_data)
            return {
                "success": True,
                "response": result.get("output", ""),
                "agent_type": "reschedule"
            }
        except Exception as e:
            return {
                "success": False,
                "response": f"Reschedule agent error: {str(e)}",
                "agent_type": "reschedule"
            }