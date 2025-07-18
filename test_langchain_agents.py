"""
MANDATORY Test Script for LangChain Agent Architecture
This script verifies that all agents are properly implemented with LangChain
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def test_langchain_imports():
    """Test that all mandatory LangChain components are available"""
    print("🧪 Testing LangChain imports...")
    
    try:
        from langchain.agents import create_openai_functions_agent, AgentExecutor
        from langchain.tools import Tool
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_community.vectorstores import Chroma
        from langchain_community.embeddings import OpenAIEmbeddings
        print("✅ All mandatory LangChain imports successful")
        return True
    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        return False

def test_agent_initialization():
    """Test that all agents can be initialized"""
    print("🤖 Testing agent initialization...")
    
    try:
        from app.agents.root_agent import RootAgent
        from app.agents.booking_agent import BookingAgent
        from app.agents.cancel_agent import CancelAgent
        from app.agents.reschedule_agent import RescheduleAgent
        from app.agents.query_agent import QueryAgent
        from app.agents.symptom_agent import SymptomAgent
        
        # Test RootAgent initialization
        root_agent = RootAgent()
        print("✅ RootAgent initialized successfully")
        
        # Test individual agents
        booking_agent = BookingAgent()
        print("✅ BookingAgent initialized successfully")
        
        cancel_agent = CancelAgent()
        print("✅ CancelAgent initialized successfully")
        
        reschedule_agent = RescheduleAgent()
        print("✅ RescheduleAgent initialized successfully")
        
        query_agent = QueryAgent()
        print("✅ QueryAgent initialized successfully")
        
        symptom_agent = SymptomAgent()
        print("✅ SymptomAgent initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False

def test_rag_system():
    """Test RAG system with ChromaDB"""
    print("📚 Testing RAG system...")
    
    try:
        from app.rag.vector_store import RAGSystem
        
        rag_system = RAGSystem()
        
        # Test knowledge base query
        response = rag_system.query_knowledge_base("What are the hospital hours?")
        print(f"✅ RAG system query successful: {response[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ RAG system test failed: {e}")
        return False

def test_database_tools():
    """Test database tools for agents"""
    print("🛠️ Testing database tools...")
    
    try:
        from app.tools.database_tools import create_booking_tools, create_query_tools
        
        booking_tools = create_booking_tools()
        print(f"✅ Booking tools created: {len(booking_tools)} tools")
        
        query_tools = create_query_tools()
        print(f"✅ Query tools created: {len(query_tools)} tools")
        
        # Test a tool function
        departments_result = booking_tools[4].func("")  # get_departments tool
        print(f"✅ Database tool test successful: {departments_result[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Database tools test failed: {e}")
        return False

def test_agent_processing():
    """Test agent processing with sample inputs"""
    print("🎯 Testing agent processing...")
    
    try:
        from app.agents.root_agent import RootAgent
        
        root_agent = RootAgent()
        
        # Test booking intent
        booking_response = root_agent.process_message("+1234567890", "I want to book an appointment")
        print(f"✅ Booking processing successful: {booking_response[:100]}...")
        
        # Test symptom intent
        symptom_response = root_agent.process_message("+1234567890", "I have chest pain")
        print(f"✅ Symptom processing successful: {symptom_response[:100]}...")
        
        # Test query intent
        query_response = root_agent.process_message("+1234567890", "What are your hours?")
        print(f"✅ Query processing successful: {query_response[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Agent processing test failed: {e}")
        return False

def main():
    """Run all LangChain agent tests"""
    print("🚀 MANDATORY LangChain Agent Architecture Test Suite")
    print("=" * 60)
    
    tests = [
        test_langchain_imports,
        test_agent_initialization,
        test_rag_system,
        test_database_tools,
        test_agent_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print("-" * 40)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print("-" * 40)
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL LANGCHAIN AGENT TESTS PASSED!")
        print("✅ System is properly implemented with LangChain architecture")
    else:
        print("⚠️ Some tests failed - LangChain architecture needs fixes")
    
    return passed == total

if __name__ == "__main__":
    main()