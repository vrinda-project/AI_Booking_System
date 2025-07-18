# LangChain Agent Architecture Documentation

## 🎯 MANDATORY LangChain Implementation

This hospital booking system is built with **STRICT ADHERENCE** to LangChain agent architecture. Every AI interaction goes through proper LangChain agents - NO simple function calls to Gemini are allowed.

## 🏗️ Agent Hierarchy

### 1. RootAgent (Main Coordinator)
- **File**: `app/agents/root_agent.py`
- **Role**: Main conversation coordinator
- **LangChain Components**:
  - `create_openai_functions_agent`
  - `AgentExecutor`
  - `ChatPromptTemplate`
  - `ChatGoogleGenerativeAI`

**Tools**:
- `classify_intent`: Classify user intent
- `route_to_booking_agent`: Route to booking
- `route_to_cancel_agent`: Route to cancellation
- `route_to_reschedule_agent`: Route to rescheduling
- `route_to_query_agent`: Route to general queries
- `route_to_symptom_agent`: Route to symptom analysis

### 2. BookingAgent
- **File**: `app/agents/booking_agent.py`
- **Role**: Handle appointment scheduling
- **LangChain Architecture**: Full agent with executor and tools

**Tools**:
- `check_doctor_availability`: Check availability
- `create_appointment`: Create appointments
- `get_patient_history`: Patient history
- `get_available_doctors`: Doctor listings
- `get_departments`: Department info
- `get_time_slots`: Available slots
- `send_sms`: Confirmation messages

### 3. CancelAgent
- **File**: `app/agents/cancel_agent.py`
- **Role**: Handle appointment cancellations
- **LangChain Architecture**: Full agent with executor and tools

**Tools**:
- `cancel_appointment`: Cancel appointments
- `get_patient_history`: Find appointments to cancel
- `send_sms`: Cancellation confirmations

### 4. RescheduleAgent
- **File**: `app/agents/reschedule_agent.py`
- **Role**: Handle appointment rescheduling
- **LangChain Architecture**: Full agent with executor and tools

**Tools**:
- `reschedule_appointment`: Reschedule appointments
- `check_doctor_availability`: Check new time availability
- `get_time_slots`: Available slots
- `send_sms`: Reschedule confirmations

### 5. QueryAgent (with RAG)
- **File**: `app/agents/query_agent.py`
- **Role**: Answer general hospital questions
- **LangChain Architecture**: Full agent with RAG integration

**Tools**:
- `query_hospital_knowledge`: RAG knowledge base queries
- `get_departments`: Department information
- `get_available_doctors`: Doctor information

### 6. SymptomAgent
- **File**: `app/agents/symptom_agent.py`
- **Role**: Analyze symptoms and recommend departments
- **LangChain Architecture**: Full agent with medical knowledge

**Tools**:
- `analyze_symptoms`: Symptom analysis
- `query_medical_knowledge`: Medical knowledge base
- `get_departments`: Available departments

## 🛠️ LangChain Tools System

### Database Tools (`app/tools/database_tools.py`)
All database operations go through LangChain tools:

```python
def create_booking_tools() -> List[Tool]:
    return [
        Tool(name="check_doctor_availability", ...),
        Tool(name="create_appointment", ...),
        Tool(name="get_patient_history", ...),
        Tool(name="get_available_doctors", ...),
        Tool(name="get_departments", ...)
    ]
```

### Notification Tools (`app/tools/notification_tools.py`)
SMS and communication tools:

```python
def create_notification_tools() -> List[Tool]:
    return [
        Tool(name="send_sms", ...)
    ]
```

### Calendar Tools (`app/tools/calendar_tools.py`)
Time slot and scheduling tools:

```python
def create_calendar_tools() -> List[Tool]:
    return [
        Tool(name="get_time_slots", ...)
    ]
```

## 📚 RAG System with ChromaDB

### RAG Implementation (`app/rag/vector_store.py`)
**MANDATORY ChromaDB integration**:

```python
class RAGSystem:
    def __init__(self):
        # REQUIRED: OpenAI embeddings
        self.embeddings = OpenAIEmbeddings()
        
        # REQUIRED: ChromaDB vector store
        self.vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=self.embeddings
        )
        
        # REQUIRED: Retrieval chain
        self.retrieval_chain = RetrievalQA.from_chain_type(
            llm=ChatGoogleGenerativeAI(),
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever()
        )
```

## 🔄 Agent Flow Architecture

### Voice Call Processing Flow:
```
1. Patient calls Twilio number
2. Twilio → FastAPI /api/twilio/voice/incoming
3. FastAPI → AIService (LangChain-based)
4. AIService → RootAgent.process_message()
5. RootAgent → classify_intent tool
6. RootAgent → route_to_[specific]_agent tool
7. Specific Agent → process with tools
8. Agent → database tools / RAG tools / notification tools
9. Response → TwilioService → Patient
```

### Agent Processing Example:
```python
# User: "I want to book an appointment"
RootAgent.classify_intent() → "booking"
RootAgent.route_to_booking_agent() → BookingAgent
BookingAgent.process() → Uses booking tools
BookingAgent → check_doctor_availability tool
BookingAgent → create_appointment tool  
BookingAgent → send_sms tool
Response → "Appointment booked successfully"
```

## 🚫 FORBIDDEN Implementations

**These are NOT allowed in this system**:
- Direct calls to `genai.GenerativeModel()`
- Simple Python functions without LangChain
- Basic if/else routing logic
- Direct database queries without tools
- Simple prompt-response patterns

## ✅ REQUIRED Implementations

**These are MANDATORY**:
- `create_openai_functions_agent` for all agents
- `AgentExecutor` for all agents
- `Tool` objects for all operations
- `ChatPromptTemplate` for all prompts
- `ChromaDB` for vector storage
- `RetrievalQA` for RAG queries
- Proper agent hierarchy and routing

## 🧪 Testing LangChain Architecture

Run the test script to verify proper implementation:

```bash
python test_langchain_agents.py
```

This verifies:
- All LangChain imports work
- All agents initialize properly
- RAG system functions
- Database tools work
- Agent processing works

## 📋 Dependencies

**MANDATORY LangChain packages**:
```
langchain==0.1.0
langchain-google-genai==1.0.0
langchain-community==0.0.13
langchain-core==0.1.0
chromadb==0.4.18
openai==1.3.0
```

## 🎯 Verification Checklist

- ✅ All agents use `create_openai_functions_agent`
- ✅ All agents have `AgentExecutor`
- ✅ All operations use LangChain `Tool` objects
- ✅ RAG system uses `ChromaDB` and `RetrievalQA`
- ✅ No direct Gemini API calls
- ✅ Proper agent hierarchy with RootAgent coordinator
- ✅ Database operations through tools only
- ✅ Agent-to-agent communication through routing tools

This system is a **true LangChain agent implementation** - not a simplified version!