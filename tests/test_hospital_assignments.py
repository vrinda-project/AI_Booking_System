import pytest
from .fixtures import create_test_hospital_db, create_test_department_db, create_test_doctor_db

async def test_assign_department_to_hospital(client, db):
    """Test assigning a department to a hospital"""
    hospital = create_test_hospital_db(db)
    department = create_test_department_db(db)
    
    response = await client.post(f"/api/hospital-assignments/assign-department?hospital_id={hospital.id}&department_id={department.id}")
    
    assert response.status_code == 200
    assert "Department assigned to hospital successfully" in response.json()["message"]
    
    # Verify the assignment
    response = await client.get("/api/doctors/departments/with-hospitals")
    data = response.json()
    assert len(data) == 1
    assert len(data[0]["hospitals"]) == 1
    assert data[0]["hospitals"][0]["id"] == hospital.id

async def test_assign_doctor_to_hospital(client, db):
    """Test assigning a doctor to a hospital"""
    hospital = create_test_hospital_db(db)
    department = create_test_department_db(db)
    doctor = create_test_doctor_db(db, department_id=department.id)
    
    response = await client.post(f"/api/hospital-assignments/assign-doctor?hospital_id={hospital.id}&doctor_id={doctor.id}")
    
    assert response.status_code == 200
    assert "Doctor assigned to hospital successfully" in response.json()["message"]

async def test_hospital_details(client, db):
    """Test getting hospital details"""
    hospital = create_test_hospital_db(db)
    department = create_test_department_db(db)
    doctor = create_test_doctor_db(db, department_id=department.id, hospital_id=hospital.id)
    
    # Assign department to hospital
    await client.post(f"/api/hospital-assignments/assign-department?hospital_id={hospital.id}&department_id={department.id}")
    
    response = await client.get(f"/api/hospital-details/{hospital.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == hospital.name
    assert "departments" in data