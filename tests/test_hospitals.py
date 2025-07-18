import pytest
from .fixtures import create_test_hospital, create_test_hospital_db
from app.models import Hospital

async def test_create_hospital(client, db):
    """Test creating a hospital"""
    hospital_data = create_test_hospital()
    response = await client.post("/api/hospitals/", json=hospital_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == hospital_data["name"]
    assert data["address"] == hospital_data["address"]
    assert data["phone"] == hospital_data["phone"]
    assert data["email"] == hospital_data["email"]
    assert data["admin_id"] == hospital_data["admin_id"]
    assert data["status"] == hospital_data["status"]
    assert "id" in data
    assert "created_at" in data

async def test_get_hospital(client, db):
    """Test getting a hospital by ID"""
    hospital = create_test_hospital_db(db)
    response = await client.get(f"/api/hospitals/{hospital.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == hospital.name
    assert data["id"] == hospital.id

async def test_get_hospital_not_found(client, db):
    """Test getting a non-existent hospital"""
    response = await client.get("/api/hospitals/999")
    assert response.status_code == 404

async def test_get_all_hospitals(client, db):
    """Test getting all hospitals"""
    # Create multiple hospitals
    hospital1 = create_test_hospital_db(db)
    hospital_data = create_test_hospital()
    hospital_data["name"] = "Second Hospital"
    hospital2 = Hospital(**hospital_data)
    db.add(hospital2)
    db.commit()
    
    response = await client.get("/api/hospitals/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == hospital1.name
    assert data[1]["name"] == "Second Hospital"

async def test_update_hospital(client, db):
    """Test updating a hospital"""
    hospital = create_test_hospital_db(db)
    update_data = {"name": "Updated Hospital Name"}
    
    response = await client.put(f"/api/hospitals/{hospital.id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Hospital Name"
    assert data["address"] == hospital.address  # Unchanged field

async def test_delete_hospital(client, db):
    """Test deleting a hospital"""
    hospital = create_test_hospital_db(db)
    
    response = await client.delete(f"/api/hospitals/{hospital.id}")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Hospital deleted successfully"
    
    # Verify it's deleted
    response = await client.get(f"/api/hospitals/{hospital.id}")
    assert response.status_code == 404