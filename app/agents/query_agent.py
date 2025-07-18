from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
from ..tools.database_tools import create_query_tools
from ..rag.vector_store import RAGSystem
from ..config import settings

class QueryAgent:
    """MANDATORY LangChain Agent for general queries with RAG"""
    
    def __init__(self):
        # REQUIRED: Use ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.google_ai_api_key,
            temperature=0.3
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
        """Create tools for query agent"""
        # RAG tool for knowledge base queries
        rag_tool = Tool(
            name="query_hospital_knowledge",
            description="Query hospital knowledge base for information about services, policies, hours, departments, etc.",
            func=self.rag_system.query_knowledge_base
        )
        
        query_tools = create_query_tools()
        
        return [rag_tool] + query_tools
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create prompt template for query agent"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are a hospital information agent. Your role is to answer general questions about hospital services, policies, hours, departments, and procedures.

QUERY HANDLING:
1. Use the knowledge base to find relevant information
2. Provide accurate and helpful responses
3. If information is not available, clearly state limitations
4. Direct patients to appropriate departments when needed

AVAILABLE TOOLS:
- query_hospital_knowledge: Search hospital knowledge base
- get_departments: Get list of hospital departments
- get_available_doctors: Get information about doctors

IMPORTANT RULES:
- Always use the knowledge base first for general information
- Provide accurate information only
- Be helpful and professional
- If you don't know something, admit it and suggest alternatives
- Do not provide medical advice

Current conversation context: {context}"""),
            ("user", "{input}"),
            ("assistant", "{agent_scratchpad}")
        ])
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process query request through LangChain agent"""
        try:
            result = self.executor.invoke(input_data)
            return {
                "success": True,
                "response": result.get("output", ""),
                "agent_type": "query"
            }
        except Exception as e:
            return {
                "success": False,
                "response": f"Query agent error: {str(e)}",
                "agent_type": "query"
            }