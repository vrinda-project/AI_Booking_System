from typing import Any, Dict

from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session

from app.api import deps
from app.services.ai_voice import AIVoiceAssistant

router = APIRouter()


@router.post("/incoming-call")
async def incoming_call(
    request: Request,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Handle incoming Twilio voice calls
    """
    form_data = await request.form()
    phone_number = form_data.get("From", "")
    
    ai_voice = AIVoiceAssistant(db)
    twiml_response = ai_voice.handle_incoming_call(phone_number)
    
    return {"twiml": twiml_response}


@router.post("/collect-patient-info")
async def collect_patient_info(
    request: Request,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Collect patient information from speech
    """
    form_data = await request.form()
    phone_number = form_data.get("From", "")
    speech_result = form_data.get("SpeechResult", "")
    
    ai_voice = AIVoiceAssistant(db)
    twiml_response = ai_voice.process_patient_info(speech_result, phone_number)
    
    return {"twiml": twiml_response}


@router.post("/appointment-options")
async def appointment_options(
    request: Request,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Process appointment options
    """
    form_data = await request.form()
    phone_number = form_data.get("From", "")
    speech_result = form_data.get("SpeechResult", "")
    
    ai_voice = AIVoiceAssistant(db)
    twiml_response = ai_voice.process_appointment_options(speech_result, phone_number)
    
    return {"twiml": twiml_response}


@router.post("/select-hospital")
async def select_hospital(
    request: Request,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Process hospital selection
    """
    form_data = await request.form()
    phone_number = form_data.get("From", "")
    speech_result = form_data.get("SpeechResult", "")
    
    ai_voice = AIVoiceAssistant(db)
    twiml_response = ai_voice.process_hospital_selection(speech_result, phone_number)
    
    return {"twiml": twiml_response}


@router.post("/select-department")
async def select_department(
    request: Request,
    hospital_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Process department selection
    """
    form_data = await request.form()
    phone_number = form_data.get("From", "")
    speech_result = form_data.get("SpeechResult", "")
    
    ai_voice = AIVoiceAssistant(db)
    twiml_response = ai_voice.process_department_selection(speech_result, phone_number, hospital_id)
    
    return {"twiml": twiml_response}


@router.post("/select-doctor")
async def select_doctor(
    request: Request,
    hospital_id: int,
    department_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Process doctor selection
    """
    form_data = await request.form()
    phone_number = form_data.get("From", "")
    speech_result = form_data.get("SpeechResult", "")
    
    ai_voice = AIVoiceAssistant(db)
    twiml_response = ai_voice.process_doctor_selection(speech_result, phone_number, hospital_id, department_id)
    
    return {"twiml": twiml_response}


@router.post("/select-date")
async def select_date(
    request: Request,
    hospital_id: int,
    department_id: int,
    doctor_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Process date selection
    """
    form_data = await request.form()
    phone_number = form_data.get("From", "")
    speech_result = form_data.get("SpeechResult", "")
    
    ai_voice = AIVoiceAssistant(db)
    twiml_response = ai_voice.process_date_selection(speech_result, phone_number, hospital_id, department_id, doctor_id)
    
    return {"twiml": twiml_response}


@router.post("/select-time")
async def select_time(
    request: Request,
    hospital_id: int,
    department_id: int,
    doctor_id: int,
    date: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Process time selection
    """
    form_data = await request.form()
    phone_number = form_data.get("From", "")
    speech_result = form_data.get("SpeechResult", "")
    
    ai_voice = AIVoiceAssistant(db)
    twiml_response = ai_voice.process_time_selection(speech_result, phone_number, hospital_id, department_id, doctor_id, date)
    
    return {"twiml": twiml_response}


@router.post("/cancel-appointment")
async def cancel_appointment(
    request: Request,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Process appointment cancellation
    """
    form_data = await request.form()
    phone_number = form_data.get("From", "")
    speech_result = form_data.get("SpeechResult", "") or form_data.get("Digits", "")
    
    ai_voice = AIVoiceAssistant(db)
    twiml_response = ai_voice.process_cancel_appointment(speech_result, phone_number)
    
    return {"twiml": twiml_response}