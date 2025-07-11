import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Hospital Booking System API" in response.json()["message"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_departments():
    response = client.get("/api/doctors/departments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_doctors():
    response = client.get("/api/doctors/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)