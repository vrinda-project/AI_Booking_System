"""
Minimal LangChain Agent Test - Avoiding problematic imports
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def test_basic_langchain():
    """Test basic LangChain functionality"""
    print("🧪 Testing basic LangChain...")
    
    try:
        from langchain.agents import initialize_agent, AgentType
        from langchain.tools import Tool
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ Basic LangChain imports successful")
        return True
    except Exception as e:
        print(f"❌ Basic LangChain import failed: {e}")
        return False

def test_simple_agent():
    """Test simple agent creation"""
    print("🤖 Testing simple agent...")
    
    try:
        from langchain.agents import initialize_agent, AgentType
        from langchain.tools import Tool
        from langchain_google_genai import ChatGoogleGenerativeAI
        from app.config import settings
        
        # Simple tool
        def simple_tool(input_str: str) -> str:
            return f"Tool received: {input_str}"
        
        tools = [
            Tool(
                name="simple_tool",
                description="A simple test tool",
                func=simple_tool
            )
        ]
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.google_ai_api_key
        )
        
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        
        print("✅ Simple agent created successfully")
        return True
    except Exception as e:
        print(f"❌ Simple agent creation failed: {e}")
        return False

def test_agent_run():
    """Test agent execution"""
    print("🎯 Testing agent execution...")
    
    try:
        from langchain.agents import initialize_agent, AgentType
        from langchain.tools import Tool
        from langchain_google_genai import ChatGoogleGenerativeAI
        from app.config import settings
        
        def booking_tool(input_str: str) -> str:
            return "Booking appointment for patient"
        
        tools = [
            Tool(
                name="book_appointment",
                description="Book an appointment",
                func=booking_tool
            )
        ]
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=settings.google_ai_api_key
        )
        
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False
        )
        
        response = agent.run("Book an appointment")
        print(f"✅ Agent execution successful: {response[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Agent execution failed: {e}")
        return False

def main():
    """Run minimal LangChain tests"""
    print("🚀 MINIMAL LangChain Agent Test")
    print("=" * 40)
    
    tests = [
        test_basic_langchain,
        test_simple_agent,
        test_agent_run
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            print("-" * 30)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            print("-" * 30)
    
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 LangChain agents working!")
    else:
        print("⚠️ Some issues remain")

if __name__ == "__main__":
    main()