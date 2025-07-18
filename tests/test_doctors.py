import pytest
from .fixtures import create_test_doctor, create_test_doctor_db, create_test_department_db, create_test_hospital_db

async def test_create_doctor(client, db):
    """Test creating a doctor"""
    department = create_test_department_db(db)
    doctor_data = create_test_doctor(department_id=department.id)
    
    response = await client.post("/api/doctor-management/doctors", json=doctor_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == doctor_data["name"]
    assert data["specialty"] == doctor_data["specialty"]
    assert data["department_id"] == department.id
    assert "id" in data

async def test_create_doctor_invalid_department(client, db):
    """Test creating a doctor with invalid department"""
    doctor_data = create_test_doctor(department_id=999)  # Non-existent department
    
    response = await client.post("/api/doctor-management/doctors", json=doctor_data)
    
    assert response.status_code == 404
    assert "Department not found" in response.json()["detail"]

async def test_update_doctor(client, db):
    """Test updating a doctor"""
    department = create_test_department_db(db)
    doctor = create_test_doctor_db(db, department_id=department.id)
    update_data = {"name": "Dr. Updated Name"}
    
    response = await client.put(f"/api/doctor-management/doctors/{doctor.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Dr. Updated Name"
    assert data["specialty"] == doctor.specialty  # Unchanged field

async def test_delete_doctor(client, db):
    """Test deleting a doctor"""
    department = create_test_department_db(db)
    doctor = create_test_doctor_db(db, department_id=department.id)
    
    response = await client.delete(f"/api/doctor-management/doctors/{doctor.id}")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Doctor deleted successfully"

async def test_get_all_doctors(client, db):
    """Test getting all doctors"""
    department = create_test_department_db(db)
    doctor = create_test_doctor_db(db, department_id=department.id)
    
    response = await client.get("/api/doctors/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == doctor.name

async def test_get_doctors_by_department(client, db):
    """Test getting doctors by department"""
    department = create_test_department_db(db)
    doctor = create_test_doctor_db(db, department_id=department.id)
    
    response = await client.get(f"/api/doctors/by-department/{department.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == doctor.name

async def test_get_doctor_availability(client, db):
    """Test getting doctor availability"""
    department = create_test_department_db(db)
    doctor = create_test_doctor_db(db, department_id=department.id)
    
    response = await client.get(f"/api/doctors/{doctor.id}/availability")
    
    assert response.status_code == 200
    data = response.json()
    assert "availability" in data

async def test_assign_doctor_to_hospital(client, db):
    """Test assigning a doctor to a hospital"""
    department = create_test_department_db(db)
    doctor = create_test_doctor_db(db, department_id=department.id)
    hospital = create_test_hospital_db(db)
    
    response = await client.post(f"/api/hospital-assignments/assign-doctor?hospital_id={hospital.id}&doctor_id={doctor.id}")
    
    assert response.status_code == 200
    assert "Doctor assigned to hospital successfully" in response.json()["message"]