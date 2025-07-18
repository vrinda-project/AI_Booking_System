from sqlalchemy.orm import Session
from typing import Dict, Any
from ..agents.root_agent import RootAgent

class AIService:
    """MANDATORY LangChain Agent-based AI Service"""
    
    def __init__(self, db: Session):
        self.db = db
        # REQUIRED: Use RootAgent with LangChain architecture
        self.root_agent = RootAgent()
    
    def process_message(self, phone: str, message: str) -> str:
        """Process message through LangChain agent hierarchy"""
        try:
            # MANDATORY: Route through RootAgent
            response = self.root_agent.process_message(phone, message)
            print(f"🎤 User said: {message}")
            print(f"🤖 AI responded: {response}")
            return response
        except Exception as e:
            error_msg = "I apologize, but I'm having trouble processing your request. Please try again or contact our staff directly."
            print(f"❌ AI Service error: {str(e)}")
            return error_msg