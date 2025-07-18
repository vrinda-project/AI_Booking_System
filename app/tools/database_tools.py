from langchain.tools import Tool
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
from ..models import Doctor, Department, Appointment, TimeSlot, Patient
from ..database import SessionLocal

def get_db_session():
    return SessionLocal()

def check_doctor_availability_db(input_str: str) -> str:
    """Check if doctor is available at specific time"""
    try:
        db = get_db_session()
        # Parse input - expecting "doctor_id:1,date:2024-01-15,time:14:00"
        params = dict(item.split(':') for item in input_str.split(','))
        doctor_id = int(params['doctor_id'])
        date_str = params['date']
        time_str = params['time']
        
        appointment_datetime = datetime.fromisoformat(f"{date_str}T{time_str}")
        
        # Check if slot exists and is available
        slot = db.query(TimeSlot).filter(
            TimeSlot.doctor_id == doctor_id,
            TimeSlot.start_time <= appointment_datetime,
            TimeSlot.end_time > appointment_datetime,
            TimeSlot.is_available == True
        ).first()
        
        db.close()
        return f"Available: {bool(slot)}"
    except Exception as e:
        return f"Error checking availability: {str(e)}"

def create_appointment_db(input_str: str) -> str:
    """Create new appointment in database"""
    try:
        db = get_db_session()
        # Parse input - expecting "patient_phone:+1234567890,doctor_id:1,datetime:2024-01-15T14:00,notes:chest pain"
        params = dict(item.split(':', 1) for item in input_str.split(','))
        
        patient_phone = params['patient_phone']
        doctor_id = int(params['doctor_id'])
        appointment_datetime = datetime.fromisoformat(params['datetime'])
        notes = params.get('notes', '')
        
        # Get or create patient
        patient = db.query(Patient).filter(Patient.phone == patient_phone).first()
        if not patient:
            patient = Patient(phone=patient_phone)
            db.add(patient)
            db.commit()
            db.refresh(patient)
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_datetime=appointment_datetime,
            notes=notes
        )
        db.add(appointment)
        
        # Mark slot as unavailable
        slot = db.query(TimeSlot).filter(
            TimeSlot.doctor_id == doctor_id,
            TimeSlot.start_time <= appointment_datetime,
            TimeSlot.end_time > appointment_datetime
        ).first()
        if slot:
            slot.is_available = False
        
        db.commit()
        db.close()
        return f"Appointment created successfully with ID: {appointment.id}"
    except Exception as e:
        return f"Error creating appointment: {str(e)}"

def get_patient_history_db(phone: str) -> str:
    """Get patient's previous appointments"""
    try:
        db = get_db_session()
        patient = db.query(Patient).filter(Patient.phone == phone).first()
        if not patient:
            db.close()
            return "No patient found with this phone number"
        
        appointments = db.query(Appointment).filter(
            Appointment.patient_id == patient.id
        ).join(Doctor).all()
        
        history = []
        for apt in appointments:
            history.append(f"Date: {apt.appointment_datetime}, Doctor: {apt.doctor.name}, Status: {apt.status}")
        
        db.close()
        return f"Patient history: {'; '.join(history) if history else 'No previous appointments'}"
    except Exception as e:
        return f"Error getting patient history: {str(e)}"

def get_available_doctors_db(department: str = "") -> str:
    """Get list of available doctors by department"""
    try:
        db = get_db_session()
        query = db.query(Doctor).filter(Doctor.is_active == True)
        
        if department:
            dept = db.query(Department).filter(Department.name.ilike(f"%{department}%")).first()
            if dept:
                query = query.filter(Doctor.department_id == dept.id)
        
        doctors = query.all()
        doctor_list = [f"ID: {d.id}, Name: {d.name}, Specialty: {d.specialty}" for d in doctors]
        
        db.close()
        return f"Available doctors: {'; '.join(doctor_list)}"
    except Exception as e:
        return f"Error getting doctors: {str(e)}"

def get_departments_db(input_str: str = "") -> str:
    """Get list of all departments"""
    try:
        db = get_db_session()
        departments = db.query(Department).all()
        dept_list = [f"ID: {d.id}, Name: {d.name}, Description: {d.description}" for d in departments]
        db.close()
        return f"Departments: {'; '.join(dept_list)}"
    except Exception as e:
        return f"Error getting departments: {str(e)}"

def create_booking_tools() -> List[Tool]:
    """Create database tools for booking agents"""
    return [
        Tool(
            name="check_doctor_availability",
            description="Check if doctor is available at specific time. Input format: 'doctor_id:1,date:2024-01-15,time:14:00'",
            func=check_doctor_availability_db
        ),
        Tool(
            name="create_appointment",
            description="Create new appointment in database. Input format: 'patient_phone:+1234567890,doctor_id:1,datetime:2024-01-15T14:00,notes:chest pain'",
            func=create_appointment_db
        ),
        Tool(
            name="get_patient_history",
            description="Get patient's previous appointments. Input: phone number",
            func=get_patient_history_db
        ),
        Tool(
            name="get_available_doctors",
            description="Get list of available doctors by department. Input: department name or empty string for all",
            func=get_available_doctors_db
        ),
        Tool(
            name="get_departments",
            description="Get list of all departments",
            func=get_departments_db
        )
    ]

def create_query_tools() -> List[Tool]:
    """Create database tools for query agents"""
    return [
        Tool(
            name="get_departments",
            description="Get list of all departments",
            func=get_departments_db
        ),
        Tool(
            name="get_available_doctors",
            description="Get list of available doctors",
            func=get_available_doctors_db
        )
    ]