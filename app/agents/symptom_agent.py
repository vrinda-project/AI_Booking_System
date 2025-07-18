from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
from ..tools.database_tools import create_query_tools
from ..rag.vector_store import RAGSystem
from ..config import settings

class SymptomAgent:
    """MANDATORY LangChain Agent for symptom analysis and department recommendations"""
    
    def __init__(self):
        # REQUIRED: Use ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.google_ai_api_key,
            temperature=0.2
        )
        
        # REQUIRED: Initialize RAG system
        self.rag_system = RAGSystem()
        
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
            max_iterations=3
        )
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for symptom agent"""
        # Symptom analysis tool
        symptom_analysis_tool = Tool(
            name="analyze_symptoms",
            description="Analyze patient symptoms and recommend appropriate department",
            func=self._analyze_symptoms
        )
        
        # RAG tool for medical knowledge
        rag_tool = Tool(
            name="query_medical_knowledge",
            description="Query medical knowledge base for symptom-related information",
            func=self.rag_system.query_knowledge_base
        )
        
        query_tools = create_query_tools()
        
        return [symptom_analysis_tool, rag_tool] + query_tools
    
    def _analyze_symptoms(self, symptoms: str) -> str:
        """Analyze symptoms and recommend department"""
        symptom_mapping = {
            "chest pain": {"department": "Cardiology", "urgency": "urgent", "reason": "Chest pain may indicate heart problems"},
            "heart": {"department": "Cardiology", "urgency": "urgent", "reason": "Heart-related symptoms require cardiac evaluation"},
            "shortness of breath": {"department": "Cardiology", "urgency": "urgent", "reason": "Breathing difficulties may indicate cardiac or pulmonary issues"},
            "fever": {"department": "General Medicine", "urgency": "routine", "reason": "Fever is a common symptom requiring general medical evaluation"},
            "headache": {"department": "General Medicine", "urgency": "routine", "reason": "Headaches are typically handled by general medicine"},
            "skin": {"department": "Dermatology", "urgency": "routine", "reason": "Skin conditions are treated by dermatology"},
            "rash": {"department": "Dermatology", "urgency": "routine", "reason": "Skin rashes require dermatological evaluation"},
            "bone": {"department": "Orthopedics", "urgency": "routine", "reason": "Bone-related issues are handled by orthopedics"},
            "joint": {"department": "Orthopedics", "urgency": "routine", "reason": "Joint problems require orthopedic evaluation"},
            "fracture": {"department": "Orthopedics", "urgency": "urgent", "reason": "Fractures need immediate orthopedic attention"},
            "child": {"department": "Pediatrics", "urgency": "routine", "reason": "Children's health issues are handled by pediatrics"},
            "baby": {"department": "Pediatrics", "urgency": "routine", "reason": "Infant health concerns require pediatric care"}
        }
        
        symptoms_lower = symptoms.lower()
        recommendations = []
        
        for symptom, info in symptom_mapping.items():
            if symptom in symptoms_lower:
                recommendations.append(f"Department: {info['department']}, Urgency: {info['urgency']}, Reason: {info['reason']}")
        
        if not recommendations:
            return "Based on the symptoms described, I recommend starting with General Medicine for initial evaluation. They can refer you to a specialist if needed."
        
        return "; ".join(recommendations)
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create prompt template for symptom agent"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are a medical triage agent. Your role is to analyze patient symptoms and recommend the most appropriate hospital department.

SYMPTOM ANALYSIS PROCESS:
1. Listen to patient's symptom description
2. Use symptom analysis tools to determine appropriate department
3. Assess urgency level (emergency, urgent, routine)
4. Provide clear recommendations
5. Always remind patients this is not a medical diagnosis

AVAILABLE TOOLS:
- analyze_symptoms: Analyze symptoms and recommend department
- query_medical_knowledge: Search medical knowledge base
- get_departments: Get list of available departments
- get_available_doctors: Get doctors by department

IMPORTANT RULES:
- Never provide medical diagnosis
- Always recommend consulting with a doctor
- Assess urgency appropriately
- For emergency symptoms (severe chest pain, difficulty breathing), recommend immediate emergency care
- Be empathetic and professional
- Explain reasoning for department recommendations

EMERGENCY SYMPTOMS (immediate attention needed):
- Severe chest pain
- Difficulty breathing
- Severe bleeding
- Loss of consciousness
- Severe allergic reactions

Current conversation context: {context}"""),
            ("user", "{input}"),
            ("assistant", "{agent_scratchpad}")
        ])
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process symptom analysis request through LangChain agent"""
        try:
            result = self.executor.invoke(input_data)
            return {
                "success": True,
                "response": result.get("output", ""),
                "agent_type": "symptom"
            }
        except Exception as e:
            return {
                "success": False,
                "response": f"Symptom agent error: {str(e)}",
                "agent_type": "symptom"
            }