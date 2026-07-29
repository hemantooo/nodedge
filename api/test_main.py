"""
Unit tests for FastAPI Workshop Registration Backend API.
Uses TestClient and unittest.mock to test endpoints and validation logic without external network calls.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check_healthy():
    """
    Test GET /api/health when Google Sheets service is healthy.
    """
    with patch("main.sheets_service.check_health", return_value=(True, 42, None)):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["total_registrations"] == 42
        assert data["google_sheets_connected"] is True
        assert data["message"] is None


def test_health_check_degraded():
    """
    Test GET /api/health when Google Sheets connection fails.
    """
    with patch("main.sheets_service.check_health", return_value=(False, 0, "Missing credentials")):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["google_sheets_connected"] is False
        assert "Missing credentials" in data["message"]


def test_register_successful():
    """
    Test POST /api/register with valid input and non-duplicate enrollment.
    """
    payload = {
        "full_name": "Alice Smith",
        "enrollment_no": "210303123045",
        "email": "alice.smith@paruluniversity.ac.in",
        "semester": "Semester 6",
        "proficiency": "Advanced",
        "reason": "Interested in Machine Learning models"
    }

    with patch("main.sheets_service.is_enrollment_registered", return_value=False), \
         patch("main.sheets_service.append_registration", return_value=[]):
        response = client.post("/api/register", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Registration successful!"
        assert "registration_id" in data
        assert len(data["registration_id"]) > 0


def test_register_duplicate_enrollment():
    """
    Test POST /api/register when enrollment number is already registered.
    """
    payload = {
        "full_name": "Bob Jones",
        "enrollment_no": "210303123045",
        "email": "bob.jones@paruluniversity.ac.in",
        "semester": "Semester 4",
        "proficiency": "Beginner",
        "reason": "Wants to learn Python"
    }

    with patch("main.sheets_service.is_enrollment_registered", return_value=True):
        response = client.post("/api/register", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Enrollment number already registered."


def test_register_invalid_email_domain():
    """
    Test POST /api/register with an email that does not end with @paruluniversity.ac.in.
    Must return HTTP 400 status.
    """
    payload = {
        "full_name": "Charlie Brown",
        "enrollment_no": "210303123099",
        "email": "charlie@gmail.com",
        "semester": "Semester 3",
        "proficiency": "Intermediate",
        "reason": "Test non-university email"
    }

    response = client.post("/api/register", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "email must end with @paruluniversity.ac.in" in data["detail"].lower()


def test_register_missing_required_field():
    """
    Test POST /api/register with missing required enrollment_no field.
    Must return HTTP 400 status.
    """
    payload = {
        "full_name": "Dave Wilson",
        # missing enrollment_no
        "email": "dave@paruluniversity.ac.in",
        "semester": "Semester 1",
        "proficiency": "Beginner",
        "reason": "Test"
    }

    response = client.post("/api/register", json=payload)
    assert response.status_code == 400
