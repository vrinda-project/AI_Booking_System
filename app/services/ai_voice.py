from typing import Dict, Any, Optional
import json
import uuid
from datetime import datetime, date, time

from sqlalchemy.orm import Session
import openai
from twilio.twiml.voice_response import VoiceResponse, Gather

from app.core.config import settings
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.hospital import Hospital
from app.models.department import Department
from app.models.appointment import Appointment


class AIVoiceAssistant:
    """AI Voice Assistant for handling appointment booking via phone calls"""
    
    def __init__(self, db: Session):
        self.db = db
        openai.api_key = settings.OPENAI_API_KEY
    
    def handle_incoming_call(self, phone_number: str) -> str:
        """Handle incoming call and return TwiML response"""
        # Check if patient exists
        patient = self.db.query(Patient).filter(Patient.phone == phone_number).first()
        
        response = VoiceResponse()
        
        if not patient:
            # New patient flow
            response.say("Welcome to our Hospital Appointment Booking System. It seems like this is your first time calling.")
            gather = Gather(input="speech", action="/api/v1/voice/collect-patient-info", method="POST")
            gather.say("Please tell me your full name.")
            response.append(gather)
            response.say("We didn't receive any input. Please call again.")
        else:
            # Existing patient flow
            response.say(f"Welcome back {patient.full_name} to our Hospital Appointment Booking System.")
            gather = Gather(input="speech", action="/api/v1/voice/appointment-options", method="POST")
            gather.say("Would you like to book a new appointment, check your existing appointments, or cancel an appointment?")
            response.append(gather)
            response.say("We didn't receive any input. Please call again.")
        
        return str(response)
    
    def process_patient_info(self, speech_result: str, phone_number: str) -> str:
        """Process patient information and create a new patient record"""
        # Use OpenAI to extract name from speech
        prompt = f"Extract the full name from this speech: '{speech_result}'"
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )
        full_name = completion.choices[0].text.strip()
        
        # Create new patient
        patient = Patient(
            full_name=full_name,
            phone=phone_number,
            created_by="ai_voice_system"
        )
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        
        response = VoiceResponse()
        response.say(f"Thank you {full_name}. Your information has been registered.")
        gather = Gather(input="speech", action="/api/v1/voice/appointment-options", method="POST")
        gather.say("Would you like to book a new appointment, check your existing appointments, or cancel an appointment?")
        response.append(gather)
        
        return str(response)
    
    def process_appointment_options(self, speech_result: str, phone_number: str) -> str:
        """Process appointment options based on speech input"""
        # Use OpenAI to understand intent
        prompt = f"Classify this speech into one of these intents: 'book_appointment', 'check_appointments', 'cancel_appointment', 'other': '{speech_result}'"
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )
        intent = completion.choices[0].text.strip().lower()
        
        response = VoiceResponse()
        
        if "book_appointment" in intent:
            # Start booking flow
            gather = Gather(input="speech", action="/api/v1/voice/select-hospital", method="POST")
            hospitals = self.db.query(Hospital).filter(Hospital.status == "active").all()
            hospital_names = ", ".join([h.name for h in hospitals])
            gather.say(f"We have the following hospitals available: {hospital_names}. Please say the name of the hospital you'd like to book with.")
            response.append(gather)
        
        elif "check_appointments" in intent:
            # Check existing appointments
            patient = self.db.query(Patient).filter(Patient.phone == phone_number).first()
            appointments = self.db.query(Appointment).filter(
                Appointment.patient_id == patient.id,
                Appointment.status.in_(["scheduled", "confirmed"])
            ).all()
            
            if not appointments:
                response.say("You don't have any upcoming appointments.")
            else:
                response.say(f"You have {len(appointments)} upcoming appointments.")
                for i, appt in enumerate(appointments):
                    doctor = self.db.query(Doctor).filter(Doctor.id == appt.doctor_id).first()
                    hospital = self.db.query(Hospital).filter(Hospital.id == appt.hospital_id).first()
                    response.say(
                        f"Appointment {i+1}: {appt.appointment_date.strftime('%B %d')} at "
                        f"{appt.appointment_time.strftime('%I:%M %p')} with Dr. {doctor.full_name} "
                        f"at {hospital.name}."
                    )
            
            response.say("Thank you for calling. Goodbye!")
        
        elif "cancel_appointment" in intent:
            # Cancel appointment flow
            patient = self.db.query(Patient).filter(Patient.phone == phone_number).first()
            appointments = self.db.query(Appointment).filter(
                Appointment.patient_id == patient.id,
                Appointment.status.in_(["scheduled", "confirmed"])
            ).all()
            
            if not appointments:
                response.say("You don't have any upcoming appointments to cancel.")
                response.say("Thank you for calling. Goodbye!")
            else:
                response.say(f"You have {len(appointments)} upcoming appointments.")
                for i, appt in enumerate(appointments):
                    doctor = self.db.query(Doctor).filter(Doctor.id == appt.doctor_id).first()
                    hospital = self.db.query(Hospital).filter(Hospital.id == appt.hospital_id).first()
                    response.say(
                        f"Appointment {i+1}: {appt.appointment_date.strftime('%B %d')} at "
                        f"{appt.appointment_time.strftime('%I:%M %p')} with Dr. {doctor.full_name} "
                        f"at {hospital.name}."
                    )
                
                gather = Gather(input="speech dtmf", action="/api/v1/voice/cancel-appointment", method="POST", numDigits=1)
                gather.say("Please say or press the number of the appointment you want to cancel.")
                response.append(gather)
        
        else:
            response.say("I'm sorry, I didn't understand that. Please call again later.")
        
        return str(response)
    
    def process_hospital_selection(self, speech_result: str, phone_number: str) -> str:
        """Process hospital selection for appointment booking"""
        # Use OpenAI to extract hospital name
        hospitals = self.db.query(Hospital).filter(Hospital.status == "active").all()
        hospital_names = [h.name for h in hospitals]
        
        prompt = f"From this speech: '{speech_result}', which hospital is being referred to from this list: {hospital_names}? Return just the hospital name."
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )
        selected_hospital = completion.choices[0].text.strip()
        
        hospital = self.db.query(Hospital).filter(Hospital.name == selected_hospital).first()
        if not hospital:
            response = VoiceResponse()
            response.say("I'm sorry, I couldn't find that hospital. Please try again.")
            return str(response)
        
        # Get departments for the hospital
        departments = self.db.query(Department).filter(
            Department.hospital_id == hospital.id,
            Department.is_active == True
        ).all()
        
        response = VoiceResponse()
        gather = Gather(input="speech", action=f"/api/v1/voice/select-department?hospital_id={hospital.id}", method="POST")
        department_names = ", ".join([d.name for d in departments])
        gather.say(f"You selected {hospital.name}. We have the following departments: {department_names}. Please say which department you need.")
        response.append(gather)
        
        return str(response)
    
    def process_department_selection(self, speech_result: str, phone_number: str, hospital_id: int) -> str:
        """Process department selection for appointment booking"""
        # Use OpenAI to extract department name
        departments = self.db.query(Department).filter(
            Department.hospital_id == hospital_id,
            Department.is_active == True
        ).all()
        department_names = [d.name for d in departments]
        
        prompt = f"From this speech: '{speech_result}', which department is being referred to from this list: {department_names}? Return just the department name."
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )
        selected_department = completion.choices[0].text.strip()
        
        department = self.db.query(Department).filter(
            Department.name == selected_department,
            Department.hospital_id == hospital_id
        ).first()
        
        if not department:
            response = VoiceResponse()
            response.say("I'm sorry, I couldn't find that department. Please try again.")
            return str(response)
        
        # Get doctors for the department
        doctors = self.db.query(Doctor).filter(
            Doctor.department_id == department.id,
            Doctor.is_active == True
        ).all()
        
        response = VoiceResponse()
        gather = Gather(
            input="speech", 
            action=f"/api/v1/voice/select-doctor?hospital_id={hospital_id}&department_id={department.id}", 
            method="POST"
        )
        doctor_names = ", ".join([f"Dr. {d.full_name}" for d in doctors])
        gather.say(f"You selected {department.name} department. We have the following doctors: {doctor_names}. Please say which doctor you'd like to see.")
        response.append(gather)
        
        return str(response)
    
    def process_doctor_selection(self, speech_result: str, phone_number: str, hospital_id: int, department_id: int) -> str:
        """Process doctor selection for appointment booking"""
        # Use OpenAI to extract doctor name
        doctors = self.db.query(Doctor).filter(
            Doctor.department_id == department_id,
            Doctor.hospital_id == hospital_id,
            Doctor.is_active == True
        ).all()
        doctor_names = [f"Dr. {d.full_name}" for d in doctors]
        
        prompt = f"From this speech: '{speech_result}', which doctor is being referred to from this list: {doctor_names}? Return just the doctor name without 'Dr.'."
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )
        selected_doctor = completion.choices[0].text.strip()
        
        # Remove "Dr." if present
        if selected_doctor.lower().startswith("dr."):
            selected_doctor = selected_doctor[3:].strip()
        
        doctor = self.db.query(Doctor).filter(
            Doctor.full_name == selected_doctor,
            Doctor.department_id == department_id
        ).first()
        
        if not doctor:
            response = VoiceResponse()
            response.say("I'm sorry, I couldn't find that doctor. Please try again.")
            return str(response)
        
        # Ask for date
        response = VoiceResponse()
        gather = Gather(
            input="speech", 
            action=f"/api/v1/voice/select-date?hospital_id={hospital_id}&department_id={department_id}&doctor_id={doctor.id}", 
            method="POST"
        )
        gather.say(f"You selected Dr. {doctor.full_name}. Please say the date you'd like to book, for example, 'June 15th'.")
        response.append(gather)
        
        return str(response)
    
    def process_date_selection(self, speech_result: str, phone_number: str, hospital_id: int, department_id: int, doctor_id: int) -> str:
        """Process date selection for appointment booking"""
        # Use OpenAI to extract date
        prompt = f"From this speech: '{speech_result}', extract the date in YYYY-MM-DD format."
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )
        date_str = completion.choices[0].text.strip()
        
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            response = VoiceResponse()
            response.say("I'm sorry, I couldn't understand the date. Please try again with a date like 'June 15th'.")
            return str(response)
        
        # Ask for time
        response = VoiceResponse()
        gather = Gather(
            input="speech", 
            action=f"/api/v1/voice/select-time?hospital_id={hospital_id}&department_id={department_id}&doctor_id={doctor_id}&date={date_str}", 
            method="POST"
        )
        gather.say(f"You selected {selected_date.strftime('%B %d, %Y')}. Please say the time you'd like to book, for example, '2:30 PM'.")
        response.append(gather)
        
        return str(response)
    
    def process_time_selection(self, speech_result: str, phone_number: str, hospital_id: int, department_id: int, doctor_id: int, date_str: str) -> str:
        """Process time selection for appointment booking"""
        # Use OpenAI to extract time
        prompt = f"From this speech: '{speech_result}', extract the time in HH:MM AM/PM format."
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50
        )
        time_str = completion.choices[0].text.strip()
        
        try:
            selected_time = datetime.strptime(time_str, "%I:%M %p").time()
        except ValueError:
            response = VoiceResponse()
            response.say("I'm sorry, I couldn't understand the time. Please try again with a time like '2:30 PM'.")
            return str(response)
        
        # Check if appointment slot is available
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Check for existing appointments
        existing_appointment = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == selected_date,
            Appointment.appointment_time == selected_time,
            Appointment.status.in_(["scheduled", "confirmed"])
        ).first()
        
        if existing_appointment:
            response = VoiceResponse()
            response.say("I'm sorry, that time slot is already booked. Please try another time.")
            return str(response)
        
        # Create the appointment
        patient = self.db.query(Patient).filter(Patient.phone == phone_number).first()
        doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
        hospital = self.db.query(Hospital).filter(Hospital.id == hospital_id).first()
        department = self.db.query(Department).filter(Department.id == department_id).first()
        
        # Generate unique booking reference
        booking_reference = f"APPT-{uuid.uuid4().hex[:8].upper()}"
        
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            hospital_id=hospital_id,
            department_id=department_id,
            appointment_date=selected_date,
            appointment_time=selected_time,
            duration_minutes=30,
            appointment_type="consultation",
            status="scheduled",
            booking_source="ai_voice",
            booking_reference=booking_reference,
            created_by="ai_voice_system"
        )
        
        self.db.add(appointment)
        self.db.commit()
        
        # Confirm appointment
        response = VoiceResponse()
        response.say(
            f"Great! Your appointment has been booked with Dr. {doctor.full_name} "
            f"at {hospital.name} on {selected_date.strftime('%B %d, %Y')} "
            f"at {selected_time.strftime('%I:%M %p')}. "
            f"Your booking reference is {booking_reference}. "
            f"Thank you for using our service!"
        )
        
        return str(response)
    
    def process_cancel_appointment(self, speech_result: str, phone_number: str) -> str:
        """Process appointment cancellation"""
        # Get the appointment number from speech or DTMF
        try:
            if speech_result.isdigit():
                appointment_num = int(speech_result)
            else:
                # Use OpenAI to extract number
                prompt = f"Extract the appointment number (as a digit) from this speech: '{speech_result}'"
                completion = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=50
                )
                appointment_num = int(completion.choices[0].text.strip())
        except (ValueError, IndexError):
            response = VoiceResponse()
            response.say("I'm sorry, I couldn't understand which appointment you want to cancel. Please try again.")
            return str(response)
        
        # Get patient's appointments
        patient = self.db.query(Patient).filter(Patient.phone == phone_number).first()
        appointments = self.db.query(Appointment).filter(
            Appointment.patient_id == patient.id,
            Appointment.status.in_(["scheduled", "confirmed"])
        ).all()
        
        if not appointments or appointment_num < 1 or appointment_num > len(appointments):
            response = VoiceResponse()
            response.say("I'm sorry, that's not a valid appointment number. Please try again.")
            return str(response)
        
        # Cancel the appointment
        appointment = appointments[appointment_num - 1]
        appointment.status = "cancelled"
        appointment.cancelled_by = "patient_via_voice"
        appointment.cancellation_reason = "Cancelled via phone"
        appointment.cancelled_at = datetime.utcnow()
        appointment.updated_by = "ai_voice_system"
        
        self.db.add(appointment)
        self.db.commit()
        
        # Confirm cancellation
        response = VoiceResponse()
        doctor = self.db.query(Doctor).filter(Doctor.id == appointment.doctor_id).first()
        response.say(
            f"Your appointment with Dr. {doctor.full_name} on "
            f"{appointment.appointment_date.strftime('%B %d, %Y')} at "
            f"{appointment.appointment_time.strftime('%I:%M %p')} has been cancelled. "
            f"Thank you for using our service!"
        )
        
        return str(response)