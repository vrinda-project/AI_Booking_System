import re
from datetime import datetime
from typing import Optional

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    pattern = r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$'
    return bool(re.match(pattern, phone.replace('-', '').replace(' ', '')))

def validate_datetime(date_str: str) -> Optional[datetime]:
    """Validate and parse datetime string"""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        return None

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    return text.strip().lower() if text else ""