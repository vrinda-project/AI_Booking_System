from langchain.tools import Tool
from typing import List
from datetime import datetime, timedelta

def get_available_time_slots(input_str: str) -> str:
    """Get available time slots for a specific date"""
    try:
        # Parse input - expecting "doctor_id:1,date:2024-01-15"
        params = dict(item.split(':') for item in input_str.split(','))
        doctor_id = int(params['doctor_id'])
        date_str = params['date']
        
        # Generate sample time slots (in real implementation, query database)
        date = datetime.fromisoformat(date_str)
        slots = []
        
        # Morning slots
        for hour in range(9, 12):
            slot_time = date.replace(hour=hour, minute=0)
            slots.append(slot_time.strftime("%H:%M"))
        
        # Afternoon slots
        for hour in range(14, 17):
            slot_time = date.replace(hour=hour, minute=0)
            slots.append(slot_time.strftime("%H:%M"))
        
        return f"Available slots: {', '.join(slots)}"
    except Exception as e:
        return f"Error getting time slots: {str(e)}"

def create_calendar_tools() -> List[Tool]:
    """Create calendar tools for agents"""
    return [
        Tool(
            name="get_time_slots",
            description="Get available time slots for a doctor on specific date. Input format: 'doctor_id:1,date:2024-01-15'",
            func=get_available_time_slots
        )
    ]