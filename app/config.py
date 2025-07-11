from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str
    redis_url: str = "redis://localhost:6379"
    
    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    
    # AI Services
    google_ai_api_key: str
    openai_api_key: str
    
    # Google Calendar
    google_calendar_client_id: Optional[str] = None
    google_calendar_client_secret: Optional[str] = None
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    
    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()