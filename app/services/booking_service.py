from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from ..models import Patient, Doctor, Appointment, TimeSlot, Department
from ..schemas import AppointmentCreate

class BookingService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_patient(self, phone: str, name: str = None) -> Patient:
        patient = self.db.query(Patient).filter(Patient.phone == phone).first()
        if not patient:
            patient = Patient(phone=phone, name=name)
            self.db.add(patient)
            self.db.commit()
            self.db.refresh(patient)
        return patient
    
    def get_available_doctors(self, department_id: int = None) -> List[Doctor]:
        query = self.db.query(Doctor).filter(Doctor.is_active == True)
        if department_id:
            query = query.filter(Doctor.department_id == department_id)
        return query.all()
    
    def get_available_slots(self, doctor_id: int, date: datetime) -> List[TimeSlot]:
        return self.db.query(TimeSlot).filter(
            TimeSlot.doctor_id == doctor_id,
            TimeSlot.date >= date.date(),
            TimeSlot.is_available == True
        ).all()
    
    def book_appointment(self, patient_phone: str, doctor_id: int, 
                        appointment_datetime: datetime, notes: str = None) -> Appointment:
        patient = self.get_or_create_patient(patient_phone)
        
        # Check if slot is available
        slot = self.db.query(TimeSlot).filter(
            TimeSlot.doctor_id == doctor_id,
            TimeSlot.start_time <= appointment_datetime,
            TimeSlot.end_time > appointment_datetime,
            TimeSlot.is_available == True
        ).first()
        
        if not slot:
            raise ValueError("Time slot not available")
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_datetime=appointment_datetime,
            notes=notes
        )
        
        # Mark slot as unavailable
        slot.is_available = False
        
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    def get_departments(self) -> List[Department]:
        return self.db.query(Department).all()