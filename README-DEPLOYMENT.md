# Deploying to Render

This guide explains how to deploy the Hospital Appointment Booking System to Render.

## Prerequisites

1. A [Render account](https://render.com/)
2. Your code pushed to a Git repository (GitHub, GitLab, etc.)

## Deployment Steps

### Option 1: Deploy using render.yaml (Recommended)

1. Connect your Git repository to Render
2. Render will automatically detect the `render.yaml` file and create the services
3. Configure the environment variables that are marked as `sync: false` in the Render dashboard:
   - `OPENAI_API_KEY`
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`

### Option 2: Manual Deployment

1. Log in to your Render account
2. Click "New" and select "Web Service"
3. Connect your Git repository
4. Configure the service:
   - **Name**: hospital-booking-api
   - **Environment**: Docker
   - **Region**: Choose the closest to your users
   - **Branch**: main (or your preferred branch)
   - **Health Check Path**: /health
   - **Plan**: Starter (or choose based on your needs)

5. Add the following environment variables:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: A secure random string
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
   - `TWILIO_PHONE_NUMBER`: Your Twilio Phone Number

6. Click "Create Web Service"

## Database Setup

If you're using the `render.yaml` approach, the PostgreSQL database will be created automatically.

For manual deployment:

1. In Render, go to "New" and select "PostgreSQL"
2. Configure your database:
   - **Name**: hospital-booking-db
   - **Database**: hospital_booking
   - **User**: hospital_booking_user
   - **Region**: Same as your web service
   - **Plan**: Starter (or choose based on your needs)

3. After creation, copy the "Internal Database URL" and set it as the `DATABASE_URL` environment variable in your web service.

## Post-Deployment

After deployment:

1. Run database migrations (if needed):
   - You can add a custom start command in your Render dashboard:
     ```
     alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

2. Seed initial data (if needed):
   - Connect to your Render service shell and run:
     ```
     python seed_data.py
     ```

3. Access your API at the URL provided by Render (e.g., https://hospital-booking-api.onrender.com)

## Monitoring and Logs

- Monitor your service in the Render dashboard
- View logs by clicking on your service and selecting the "Logs" tab
- Set up alerts for errors or high resource usage