from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, get_db
from .database import Base
from .api import twilio_router, appointments_router, doctors_router, hospitals_router, hospital_assignments_router, hospital_details_router, db_view_router, doctor_management_router, department_management_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Hospital Booking System",
    description="Voice-powered appointment booking system with Twilio integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(twilio_router)
app.include_router(appointments_router)
app.include_router(doctors_router)
app.include_router(hospitals_router)
app.include_router(hospital_assignments_router)
app.include_router(hospital_details_router)
app.include_router(db_view_router)
app.include_router(doctor_management_router)
app.include_router(department_management_router)

@app.get("/")
async def root():
    return {
        "message": "AI Hospital Booking System API",
        "version": "1.0.0",
        "endpoints": {
            "twilio_webhook": "/api/twilio/voice/incoming",
            "appointments": "/api/appointments",
            "doctors": "/api/doctors"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Initialize sample data and LangChain agents
@app.on_event("startup")
async def startup_event():
    """Initialize sample data and LangChain agent system on startup"""
    print("🚀 Initializing LangChain Agent-based Hospital Booking System...")
    
    # Initialize database
    db = next(get_db())
    
    # Check if departments exist
    from .models import Department, Doctor, TimeSlot
    from datetime import datetime, timedelta
    
    if db.query(Department).count() == 0:
        # Create sample departments
        departments = [
            Department(name="General Medicine", description="General health checkups and common illnesses"),
            Department(name="Cardiology", description="Heart and cardiovascular conditions"),
            Department(name="Pediatrics", description="Children's health and development"),
            Department(name="Orthopedics", description="Bone, joint, and muscle conditions"),
            Department(name="Dermatology", description="Skin conditions and treatments")
        ]
        
        for dept in departments:
            db.add(dept)
        db.commit()
        
        # Create sample doctors
        doctors = [
            Doctor(name="Dr. Sarah Johnson", specialty="General Practitioner", department_id=1),
            Doctor(name="Dr. Michael Chen", specialty="Cardiologist", department_id=2),
            Doctor(name="Dr. Emily Rodriguez", specialty="Pediatrician", department_id=3),
            Doctor(name="Dr. David Kim", specialty="Orthopedic Surgeon", department_id=4),
            Doctor(name="Dr. Lisa Thompson", specialty="Dermatologist", department_id=5)
        ]
        
        for doctor in doctors:
            db.add(doctor)
        db.commit()
        
        # Create sample time slots for next 7 days
        for doctor in doctors:
            for day in range(7):
                date = datetime.now() + timedelta(days=day)
                # Create morning slots (9 AM - 12 PM)
                for hour in range(9, 12):
                    start_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    end_time = start_time + timedelta(hours=1)
                    
                    slot = TimeSlot(
                        doctor_id=doctor.id,
                        date=date,
                        start_time=start_time,
                        end_time=end_time,
                        is_available=True
                    )
                    db.add(slot)
                
                # Create afternoon slots (2 PM - 5 PM)
                for hour in range(14, 17):
                    start_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    end_time = start_time + timedelta(hours=1)
                    
                    slot = TimeSlot(
                        doctor_id=doctor.id,
                        date=date,
                        start_time=start_time,
                        end_time=end_time,
                        is_available=True
                    )
                    db.add(slot)
        
        db.commit()
        print("✅ Sample data initialized successfully!")
    
    # Initialize LangChain agent system
    try:
        from .agents.root_agent import RootAgent
        root_agent = RootAgent()
        print("✅ LangChain agent system initialized successfully!")
        print("🤖 Available agents: RootAgent, BookingAgent, CancelAgent, RescheduleAgent, QueryAgent, SymptomAgent")
        print("📚 RAG system with ChromaDB initialized")
        print("🛠️ Database tools for agents ready")
    except Exception as e:
        print(f"⚠️ Warning: LangChain agent initialization failed: {e}")
    
    db.close()

if __name__ == "__main__":
    import uvicorn
    from .config import settings
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)