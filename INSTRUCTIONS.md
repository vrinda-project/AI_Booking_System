# Instructions for Database Migration and Seeding

## Prerequisites

Make sure you have installed all the required packages:

```bash
pip install -r requirements.txt
```

## Step 1: Run Alembic Migration

To update the database schema with the new "agent" role:

```bash
# Navigate to the project directory
cd path/to/AI_booking_system

# Run the migration
alembic upgrade head
```

This will apply the migration that adds the "agent" role to the user_role enum.

## Step 2: Seed the Database

To populate the database with demo users:

```bash
# Navigate to the project directory
cd path/to/AI_booking_system

# Run the seed script
python seed_data.py
```

This will create the following demo users:

1. Super Admin:
   - Email: admin@hospital.com
   - Password: password123
   - Role: super_admin

2. Hospital Admin:
   - Email: hospital@admin.com
   - Password: password123
   - Role: hospital_admin

3. Doctor:
   - Email: doctor@hospital.com
   - Password: password123
   - Role: doctor

4. Booking Agent:
   - Email: agent@hospital.com
   - Password: password123
   - Role: agent

5. Patient:
   - Email: patient@hospital.com
   - Password: password123
   - Role: patient

## Troubleshooting

If you encounter any issues with the migration:

1. For PostgreSQL enum issues:
   - You might need to manually update the enum using SQL:
   ```sql
   ALTER TYPE user_role ADD VALUE 'agent' AFTER 'doctor';
   ```

2. If the seed script fails:
   - Check the database connection in the .env file
   - Ensure the database is running and accessible
   - Check for any error messages in the console output