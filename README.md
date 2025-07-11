# AI-Powered Hospital Appointment Booking System

A comprehensive voice-enabled appointment booking system using Twilio, FastAPI, and Google Gemini AI.

## Features

- 🎙️ Voice-based appointment booking via Twilio
- 🤖 AI-powered conversation handling with Google Gemini
- 📅 Smart appointment scheduling and management
- 🏥 Multi-department and doctor management
- 💬 Symptom-based doctor recommendations
- 📱 SMS confirmations and notifications
- 🌐 RESTful API for integration

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd Ai_Booking_System

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials:
# - Database URL (PostgreSQL)
# - Twilio credentials
# - Google AI API key
# - Other configuration
```

### 3. Database Setup

**Option A: Docker (Recommended)**
```bash
docker-compose up -d postgres redis
```

**Option B: Local PostgreSQL**
```bash
# Install PostgreSQL locally and create database
createdb hospital_booking
```

### 4. Run Migrations

```bash
# Initialize Alembic (first time only)
alembic init migrations

# Create and run migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 5. Start the Application

```bash
# Development mode
uvicorn app.main:app --reload --port 8000

# Or using Docker
docker-compose up
```

## API Endpoints

### Twilio Integration
- `POST /api/twilio/voice/incoming` - Handle incoming calls
- `POST /api/twilio/voice/gather` - Process speech input
- `POST /api/twilio/sms/send` - Send SMS notifications

### Appointments
- `GET /api/appointments/availability` - Check doctor availability
- `POST /api/appointments/book` - Book new appointment
- `GET /api/appointments/patient/{phone}` - Get patient appointments
- `PUT /api/appointments/{id}/reschedule` - Reschedule appointment
- `DELETE /api/appointments/{id}` - Cancel appointment

### Doctors & Departments
- `GET /api/doctors` - List all doctors
- `GET /api/doctors/by-department/{id}` - Doctors by department
- `GET /api/doctors/{id}/availability` - Doctor schedule
- `GET /api/doctors/departments` - List departments

## Twilio Setup

1. Create a Twilio account and get your credentials
2. Purchase a phone number
3. Configure webhooks in Twilio Console:
   - Voice webhook: `https://your-domain.com/api/twilio/voice/incoming`
   - Method: POST

## Testing the Voice System

1. Call your Twilio phone number
2. Try these voice commands:
   - "I want to book an appointment"
   - "Schedule me with Dr. Johnson"
   - "I have chest pain, which doctor should I see?"
   - "Cancel my appointment"

## Sample Voice Conversation

```
AI: Hello! Welcome to City Hospital. How can I help you today?
User: I want to book an appointment
AI: I'd be happy to help you book an appointment. What's your name?
User: John Smith
AI: Thank you, John. Which doctor or department would you prefer?
User: I need to see a cardiologist
AI: I can schedule you with Dr. Michael Chen, our cardiologist. What date works for you?
User: Tomorrow at 2 PM
AI: Perfect! I'm booking your appointment with Dr. Chen for tomorrow at 2 PM. You'll receive a confirmation SMS shortly.
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Twilio Voice  │───▶│   FastAPI App   │───▶│   PostgreSQL    │
│   Integration   │    │   + AI Service  │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Google Gemini  │
                       │   AI Service    │
                       └─────────────────┘
```

## Deployment

### Render Deployment

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5. Add environment variables in Render dashboard

### Environment Variables for Production

```env
DATABASE_URL=postgresql://user:pass@host:5432/db
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
GOOGLE_AI_API_KEY=your_gemini_key
JWT_SECRET_KEY=your_secret_key
```

## Development

### Adding New Features

1. **New AI Agent**: Add to `app/ai/agents/`
2. **New API Route**: Add to `app/api/`
3. **New Model**: Add to `app/models/`
4. **New Service**: Add to `app/services/`

### Database Changes

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

### Testing

```bash
# Run tests
pytest

# Test specific endpoint
curl -X POST http://localhost:8000/api/appointments/book \
  -H "Content-Type: application/json" \
  -d '{"patient_phone": "+1234567890", "doctor_id": 1, "appointment_datetime": "2024-01-15T10:00:00"}'
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check DATABASE_URL in .env
   - Ensure PostgreSQL is running
   - Verify database exists

2. **Twilio Webhook Not Working**
   - Check webhook URL is publicly accessible
   - Verify Twilio credentials
   - Check webhook configuration in Twilio Console

3. **AI Not Responding**
   - Verify Google AI API key
   - Check API quotas and limits
   - Review conversation logs

### Logs and Monitoring

```bash
# View application logs
docker-compose logs app

# Monitor database
docker-compose logs postgres

# Check Redis
docker-compose logs redis
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please contact [your-email@example.com] or create an issue in the repository.