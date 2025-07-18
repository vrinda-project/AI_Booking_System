from app.models import Hospital, Department, Doctor

# Hospital test data
def create_test_hospital():
    return {
        "name": "Test Hospital",
        "address": "123 Test St",
        "phone": "555-1234",
        "email": "test@hospital.com",
        "admin_id": "admin123",
        "status": "active"
    }

def create_test_hospital_db(db):
    hospital_data = create_test_hospital()
    hospital = Hospital(**hospital_data)
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital

# Department test data
def create_test_department():
    return {
        "name": "Test Department",
        "description": "Test department description"
    }

def create_test_department_db(db):
    department_data = create_test_department()
    department = Department(**department_data)
    db.add(department)
    db.commit()
    db.refresh(department)
    return department

# Doctor test data
def create_test_doctor(department_id=1, hospital_id=None):
    return {
        "name": "Dr. Test Doctor",
        "specialty": "Test Specialty",
        "department_id": department_id,
        "hospital_id": hospital_id,
        "is_active": True
    }

def create_test_doctor_db(db, department_id=1, hospital_id=None):
    doctor_data = create_test_doctor(department_id, hospital_id)
    doctor = Doctor(**doctor_data)
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor