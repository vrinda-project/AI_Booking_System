# AI-Powered Hospital Appointment Booking System

A multi-tenant hospital management system with AI voice assistant capabilities for appointment booking.

## Features

- Multi-tenant Architecture - Hospital data isolation
- JWT Authentication with role-based access control
- AI Integration - Voice calls via Twilio + OpenAI
- Real-time Appointment Booking - No double booking
- Comprehensive API - RESTful endpoints for all operations
- Audit Logging - Track all CRUD operations
- Role-based Permissions - Super Admin → Hospital Admin → Doctor → Patient

## System Architecture

- **Super Admins**: Manage the entire platform
- **Hospitals**: Register and manage their operations
- **Departments**: Each Hospital has multiple Departments
- **Doctors**: Each Department has multiple Doctors
- **Patients**: Can book appointments with doctors
- **AI Voice Assistant**: Handles appointment booking through phone calls

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Configure environment variables in `.env` file
6. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Database
DATABASE_URI=sqlite:///./hospital_booking.db

# Security
SECRET_KEY=your_secret_key_here

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Twilio
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
```

## Database Schema

The system uses the following core tables:
- users - Authentication & role management
- hospitals - Hospital information & admin assignment
- departments - Medical departments (Cardiology, etc.)
- doctors - Doctor profiles with specializations
- patients - Patient information for bookings
- appointments - Appointment scheduling & management