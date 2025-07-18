from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
from .booking_agent import BookingAgent
from .cancel_agent import CancelAgent
from .reschedule_agent import RescheduleAgent
from .query_agent import QueryAgent
from .symptom_agent import SymptomAgent
from ..config import settings

class RootAgent:
    """MANDATORY Root Agent - Main conversation coordinator using LangChain"""
    
    def __init__(self):
        # REQUIRED: Use ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.google_ai_api_key,
            temperature=0.1
        )
        
        # REQUIRED: Initialize all sub-agents
        self.booking_agent = BookingAgent()
        self.cancel_agent = CancelAgent()
        self.reschedule_agent = RescheduleAgent()
        self.query_agent = QueryAgent()
        self.symptom_agent = SymptomAgent()
        
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
            max_iterations=3
        )
        
        # Conversation context storage
        self.conversations = {}
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for root agent"""
        return [
            Tool(
                name="classify_intent",
                description="Classify user intent into: booking, cancel, reschedule, query, symptom",
                func=self._classify_user_intent
            ),
            Tool(
                name="route_to_booking_agent",
                description="Route request to booking agent for appointment scheduling",
                func=self._route_to_booking
            ),
            Tool(
                name="route_to_cancel_agent", 
                description="Route request to cancel agent for appointment cancellation",
                func=self._route_to_cancel
            ),
            Tool(
                name="route_to_reschedule_agent",
                description="Route request to reschedule agent for appointment rescheduling",
                func=self._route_to_reschedule
            ),
            Tool(
                name="route_to_query_agent",
                description="Route request to query agent for general hospital information",
                func=self._route_to_query
            ),
            Tool(
                name="route_to_symptom_agent",
                description="Route request to symptom agent for medical symptom analysis",
                func=self._route_to_symptom
            )
        ]
    
    def _classify_user_intent(self, user_input: str) -> str:
        """Classify user intent using LangChain agent"""
        classification_prompt = f"""
        Classify the following user message into ONE of these categories:
        - booking: User wants to book/schedule a new appointment
        - cancel: User wants to cancel an existing appointment
        - reschedule: User wants to reschedule/change an existing appointment
        - query: User has general questions about hospital services, hours, policies
        - symptom: User is describing medical symptoms and needs department recommendation
        
        User message: "{user_input}"
        
        Respond with only the category name (booking, cancel, reschedule, query, or symptom).
        """
        
        try:
            response = self.llm.invoke(classification_prompt)
            intent = response.content.strip().lower()
            print(f"🧠 Root Agent classified intent: '{user_input}' -> {intent}")
            return intent
        except Exception as e:
            print(f"Error classifying intent: {e}")
            return "query"  # Default to query if classification fails
    
    def _route_to_booking(self, user_input: str) -> str:
        """Route to booking agent"""
        try:
            result = self.booking_agent.process({"input": user_input, "context": ""})
            return result.get("response", "Booking agent processing failed")
        except Exception as e:
            return f"Booking routing error: {str(e)}"
    
    def _route_to_cancel(self, user_input: str) -> str:
        """Route to cancel agent"""
        try:
            result = self.cancel_agent.process({"input": user_input, "context": ""})
            return result.get("response", "Cancel agent processing failed")
        except Exception as e:
            return f"Cancel routing error: {str(e)}"
    
    def _route_to_reschedule(self, user_input: str) -> str:
        """Route to reschedule agent"""
        try:
            result = self.reschedule_agent.process({"input": user_input, "context": ""})
            return result.get("response", "Reschedule agent processing failed")
        except Exception as e:
            return f"Reschedule routing error: {str(e)}"
    
    def _route_to_query(self, user_input: str) -> str:
        """Route to query agent"""
        try:
            result = self.query_agent.process({"input": user_input, "context": ""})
            return result.get("response", "Query agent processing failed")
        except Exception as e:
            return f"Query routing error: {str(e)}"
    
    def _route_to_symptom(self, user_input: str) -> str:
        """Route to symptom agent"""
        try:
            result = self.symptom_agent.process({"input": user_input, "context": ""})
            return result.get("response", "Symptom agent processing failed")
        except Exception as e:
            return f"Symptom routing error: {str(e)}"
    
    def _create_prompt(self) -> str:
        """Create prompt template for root agent"""
        return """You are the main hospital AI assistant coordinator. Route patients to the appropriate specialized agent based on their needs.

Use the available tools to classify intent and route to the correct agent.

Be professional and helpful."""
    
    def get_conversation_context(self, phone: str) -> Dict:
        """Get conversation context for a phone number"""
        if phone not in self.conversations:
            self.conversations[phone] = {
                'messages': [],
                'current_agent': None,
                'session_data': {}
            }
        return self.conversations[phone]
    
    def process_message(self, phone: str, message: str) -> str:
        """Main entry point for processing user messages"""
        try:
            context = self.get_conversation_context(phone)
            context['messages'].append({'role': 'user', 'content': message})
            
            # Process through root agent
            result = self.agent.invoke({
                "input": message,
                "context": str(context)
            })
            
            response = result.get("output", "I'm sorry, I couldn't process your request. Please try again.")
            context['messages'].append({'role': 'assistant', 'content': response})
            
            print(f"🤖 Root Agent response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error processing your request. Please try again or contact our staff directly."
            print(f"❌ Root Agent error: {str(e)}")
            return error_msg
    
    def route_to_agent(self, user_input: str, context: Dict) -> Dict:
        """REQUIRED: Route to appropriate agent based on intent"""
        try:
            # Use LangChain agent to determine routing
            result = self.agent.invoke({
                "input": user_input,
                "context": str(context)
            })
            
            return {
                "success": True,
                "response": result.get("output", ""),
                "agent_type": "root"
            }
        except Exception as e:
            return {
                "success": False,
                "response": f"Root agent routing error: {str(e)}",
                "agent_type": "root"
            }