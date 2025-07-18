import pytest
from .fixtures import create_test_department, create_test_department_db, create_test_doctor_db

async def test_create_department(client, db):
    """Test creating a department"""
    department_data = create_test_department()
    response = await client.post("/api/department-management/departments", json=department_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == department_data["name"]
    assert data["description"] == department_data["description"]
    assert "id" in data

async def test_update_department(client, db):
    """Test updating a department"""
    department = create_test_department_db(db)
    update_data = {"name": "Updated Department Name"}
    
    response = await client.put(f"/api/department-management/departments/{department.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Department Name"
    assert data["description"] == department.description  # Unchanged field

async def test_delete_department(client, db):
    """Test deleting a department"""
    department = create_test_department_db(db)
    
    response = await client.delete(f"/api/department-management/departments/{department.id}")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Department deleted successfully"

async def test_delete_department_with_doctors(client, db):
    """Test deleting a department that has doctors (should fail)"""
    department = create_test_department_db(db)
    doctor = create_test_doctor_db(db, department_id=department.id)
    
    response = await client.delete(f"/api/department-management/departments/{department.id}")
    
    assert response.status_code == 400
    assert "Cannot delete department with" in response.json()["detail"]

async def test_get_departments(client, db):
    """Test getting all departments"""
    department = create_test_department_db(db)
    
    response = await client.get("/api/doctors/departments")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == department.name

async def test_get_departments_with_hospitals(client, db):
    """Test getting departments with their hospital assignments"""
    department = create_test_department_db(db)
    
    response = await client.get("/api/doctors/departments/with-hospitals")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == department.name
    assert "hospitals" in data[0]