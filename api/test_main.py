"""
Unit tests for FastAPI Workshop Registration Backend API.
Uses TestClient and unittest.mock to test endpoints and validation logic without external network calls.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from api.index import app

client = TestClient(app)


def test_health_check_healthy():
    """
    Test GET /api/health when Google Sheets service is healthy.
    """
    with patch("api.index.sheets_service.check_health", return_value=(True, 42, None)):
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
    with patch("api.index.sheets_service.check_health", return_value=(False, 0, "Missing credentials")):
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
        "has_mac": "yes"
    }

    with patch("api.index.sheets_service.is_enrollment_registered", return_value=False), \
         patch("api.index.sheets_service.append_registration", return_value=[]):
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
        "has_mac": "yes"
    }

    with patch("api.index.sheets_service.is_enrollment_registered", return_value=True):
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
        "has_mac": "no"
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
        "has_mac": "no"
    }

    response = client.post("/api/register", json=payload)
    assert response.status_code == 400


def test_mark_attendance_successful():
    """
    Test POST /api/attendance/mark with valid registration ID and correct PIN.
    """
    payload = {
        "registration_id": "test_id_123",
        "pin": "1234"
    }
    mock_student = {
        "full_name": "Alice Smith",
        "enrollment_no": "210303123045",
        "email": "alice.smith@paruluniversity.ac.in",
        "semester": "Semester 6",
        "proficiency": "Advanced",
        "registration_id": "test_id_123",
        "attendance": "Absent"
    }
    mock_updated_student = mock_student.copy()
    mock_updated_student["attendance"] = "Present"

    with patch("api.index.sheets_service.get_student_by_registration_id", return_value=(2, mock_student)), \
         patch("api.index.sheets_service.mark_attendance", return_value=mock_updated_student):
        response = client.post("/api/attendance/mark", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["full_name"] == "Alice Smith"
        assert data["attendance"] == "Present"


def test_mark_attendance_already_marked():
    """
    Test POST /api/attendance/mark when attendee is already present.
    """
    payload = {
        "registration_id": "test_id_123",
        "pin": "1234"
    }
    mock_student = {
        "full_name": "Alice Smith",
        "enrollment_no": "210303123045",
        "email": "alice.smith@paruluniversity.ac.in",
        "semester": "Semester 6",
        "proficiency": "Advanced",
        "registration_id": "test_id_123",
        "attendance": "Present"
    }

    with patch("api.index.sheets_service.get_student_by_registration_id", return_value=(2, mock_student)):
        response = client.post("/api/attendance/mark", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "already_marked"
        assert "already checked in" in data["message"]


def test_mark_attendance_invalid_pin():
    """
    Test POST /api/attendance/mark with incorrect PIN.
    """
    payload = {
        "registration_id": "test_id_123",
        "pin": "wrong_pin"
    }
    response = client.post("/api/attendance/mark", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid coordinator PIN code."


def test_mark_attendance_not_found():
    """
    Test POST /api/attendance/mark with non-existing registration ID.
    """
    payload = {
        "registration_id": "non_existent",
        "pin": "1234"
    }
    with patch("api.index.sheets_service.get_student_by_registration_id", return_value=None):
        response = client.post("/api/attendance/mark", json=payload)
        assert response.status_code == 404
        assert response.json()["detail"] == "Registration ID not found."


def test_get_stats_successful():
    """
    Test GET /api/attendance/stats with correct PIN.
    """
    with patch("api.index.sheets_service.get_attendance_stats", return_value=(10, 4)):
        response = client.get("/api/attendance/stats?pin=1234")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["total_registrations"] == 10
        assert data["checked_in_count"] == 4


def test_get_stats_invalid_pin():
    """
    Test GET /api/attendance/stats with invalid PIN.
    """
    response = client.get("/api/attendance/stats?pin=wrong")
    assert response.status_code == 403
