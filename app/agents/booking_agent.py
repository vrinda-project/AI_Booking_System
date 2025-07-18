from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
from ..tools.database_tools import create_booking_tools
from ..tools.notification_tools import create_notification_tools
from ..tools.calendar_tools import create_calendar_tools
from ..config import settings

class BookingAgent:
    """MANDATORY LangChain Agent for appointment booking"""
    
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
        
        # MANDATORY: Use LangChain agent initialization
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=5
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for booking agent"""
        booking_tools = create_booking_tools()
        notification_tools = create_notification_tools()
        calendar_tools = create_calendar_tools()
        
        return booking_tools + notification_tools + calendar_tools
    
    def _create_prompt(self) -> str:
        """Create prompt template for booking agent"""
        return """You are a professional hospital appointment booking agent. Help patients book appointments efficiently.

Use the available tools to:
1. Check doctor availability
2. Create appointments
3. Send confirmations

Be professional and collect all required information."""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process booking request through LangChain agent"""
        try:
            result = self.agent.invoke({"input": input_data.get("input", "")})
            return {
                "success": True,
                "response": result.get("output", ""),
                "agent_type": "booking"
            }
        except Exception as e:
            return {
                "success": False,
                "response": f"I can help you book an appointment. Please provide your name, preferred doctor, and date.",
                "agent_type": "booking"
            }