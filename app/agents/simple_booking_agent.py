from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
# from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
from ..config import settings

class SimpleBookingAgent:
    """Simplified LangChain Agent for appointment booking"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.google_ai_api_key,
            temperature=0.1
        )
        
        self.tools = self._create_tools()
        
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create simple tools"""
        return [
            Tool(
                name="book_appointment",
                description="Book an appointment for a patient",
                func=self._book_appointment
            ),
            Tool(
                name="check_availability",
                description="Check doctor availability",
                func=self._check_availability
            )
        ]
    
    def _book_appointment(self, input_str: str) -> str:
        """Simple booking function"""
        return f"Appointment booked successfully for: {input_str}"
    
    def _check_availability(self, input_str: str) -> str:
        """Simple availability check"""
        return f"Checking availability for: {input_str}. Available slots: 9 AM, 2 PM, 4 PM"
    
    def process(self, user_input: str) -> str:
        """Process user input through agent"""
        try:
            response = self.agent.run(user_input)
            return response
        except Exception as e:
            return f"Error processing request: {str(e)}"