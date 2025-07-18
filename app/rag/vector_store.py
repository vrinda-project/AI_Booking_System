from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict
from ..config import settings

class RAGSystem:
    """Simplified RAG System"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.google_ai_api_key
        )
        
        # Simple knowledge base
        self.knowledge_base = {
            "hours": "City Hospital operates 24/7 for emergency services. Regular appointments are available Monday through Friday, 8 AM to 6 PM.",
            "cardiology": "Our Cardiology department specializes in heart conditions, chest pain, blood pressure issues, and cardiovascular diseases.",
            "pediatrics": "The Pediatrics department handles all children's health issues, from infants to teenagers, including vaccinations and checkups.",
            "orthopedics": "Orthopedics department treats bone fractures, joint problems, sports injuries, and muscle-related conditions.",
            "dermatology": "Dermatology department handles skin conditions, rashes, acne, moles, and cosmetic skin treatments.",
            "general": "General Medicine department provides routine checkups, common illnesses, fever, cold, flu, and general health consultations."
        }
    

    
    def query_knowledge_base(self, question: str) -> str:
        """Query the simplified knowledge base"""
        try:
            question_lower = question.lower()
            
            # Simple keyword matching
            for key, info in self.knowledge_base.items():
                if key in question_lower:
                    return info
            
            # Default response using LLM
            prompt = f"Answer this hospital question based on general knowledge: {question}"
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return "I can help you with information about our hospital services, hours, and departments. Please ask me about specific topics."
    
    def add_knowledge(self, key: str, text: str):
        """Add new knowledge to the knowledge base"""
        self.knowledge_base[key] = text