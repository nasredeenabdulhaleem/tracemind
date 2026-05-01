import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test123!@#"
        }
    )
    assert response.status_code == 201
    assert "id" in response.json()

def test_login_user():
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "Test123!@#"
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "Test123!@#"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_invalid_login():
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401

# Made with Bob
