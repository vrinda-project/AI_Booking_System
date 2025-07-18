import pytest
from httpx import AsyncClient
from app.main import app

# Use AsyncClient instead of TestClient for newer FastAPI versions
@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "AI Hospital Booking System API" in response.json()["message"]

async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

async def test_get_departments(client):
    response = await client.get("/api/doctors/departments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_get_doctors(client):
    response = await client.get("/api/doctors/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)