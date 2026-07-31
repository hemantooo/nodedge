"""
Main FastAPI Application Entry Point for Workshop Registration Backend Server.
Handles CORS, validation, duplicate prevention, registration submission, and health checks.
"""

import hashlib
import os
import sys
import time
from typing import Any, Dict

# Add parent directory to sys.path to allow absolute imports of the api package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Request, status, BackgroundTasks
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.schemas import (
    HealthResponse,
    RegistrationRequest,
    RegistrationResponse,
    AttendanceRequest,
    AttendanceResponse,
    StatsResponse,
    AdminProcessRequest,
    AdminProcessResponse,
)
from api.sheets_service import sheets_service
from api.email_service import send_ticket_email, send_rejection_email

# Initialize FastAPI application
print("Starting FastAPI Backend Server on Vercel...")
app = FastAPI(
    title="Workshop Registration Backend API",
    description="FastAPI backend server for syncing student workshop registrations to Google Sheets.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS Middleware
# Accepts requests from all origins or localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to ["http://localhost:3000"] in strict production if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Custom exception handler to return HTTP 400 for validation errors (e.g., email domain mismatch).
    """
    errors = exc.errors()
    error_messages = []
    for error in errors:
        msg = error.get("msg", "Invalid field input")
        # Strip internal Pydantic prefix if present
        if msg.startswith("Value error, "):
            msg = msg.replace("Value error, ", "")
        error_messages.append(msg)

    combined_message = "; ".join(error_messages)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": combined_message},
    )


def generate_registration_id(enrollment_no: str) -> str:
    """
    Generates a unique registration hash based on enrollment number and timestamp.
    """
    raw = f"{enrollment_no}:{time.time_ns()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


@app.post(
    "/api/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Workshop Registration",
    description="Validates student details, checks for duplicate enrollment, and appends record to Google Sheet.",
)
async def register_student(request: RegistrationRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Handles student registration POST requests.
    """
    # 1. Check duplicate enrollment number in Google Sheet
    try:
        if sheets_service.is_enrollment_registered(request.enrollment_no):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enrollment number already registered.",
            )
    except HTTPException:
        raise
    except Exception as exc:
        # If Google Sheets service is unconfigured or unreachable
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google Sheets service error: {str(exc)}",
        )

    # 2. Generate unique registration hash ID
    registration_id = generate_registration_id(request.enrollment_no)

    # 3. Append new row to Google Sheet
    try:
        sheets_service.append_registration(
            full_name=request.full_name,
            enrollment_no=request.enrollment_no,
            email=request.email,
            class_name=request.class_name,
            phone_number=request.phone_number,
            has_mac=request.has_mac,
            registration_id=registration_id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to append registration data to Google Sheet: {str(exc)}",
        )

    # 4. Return success response
    response = {
        "status": "success",
        "message": "Registration successful!",
        "registration_id": registration_id,
    }
    return response


@app.get(
    "/api/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Backend & Google Sheets Health Status",
    description="Returns backend status and total registration count from Google Sheet.",
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint returning connection status and total registered count.
    """
    is_connected, total_count, err_msg = sheets_service.check_health()

    if not is_connected:
        return {
            "status": "degraded",
            "total_registrations": 0,
            "google_sheets_connected": False,
            "message": f"Google Sheets connection issue: {err_msg}",
        }

    return {
        "status": "healthy",
        "total_registrations": total_count,
        "google_sheets_connected": True,
        "message": None,
    }


# Coordinator Pin Configuration
COORDINATOR_PIN = os.getenv("COORDINATOR_PIN", "1234")


@app.post(
    "/api/attendance/mark",
    response_model=AttendanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark Attendee Attendance",
    description="Validates coordinator PIN, checks registration ID in sheet, and marks student as Present.",
)
async def mark_attendance(request: AttendanceRequest) -> Dict[str, Any]:
    """
    Handles marking attendance.
    """
    if request.pin != COORDINATOR_PIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid coordinator PIN code.",
        )

    try:
        res = sheets_service.get_student_by_registration_id(request.registration_id)
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registration ID not found.",
            )

        row_idx, student = res
        if student["attendance"].strip().lower() == "present":
            return {
                "status": "already_marked",
                "message": f"{student['full_name']} is already checked in.",
                **student
            }

        updated_student = sheets_service.mark_attendance(request.registration_id, "Present")
        if not updated_student:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update attendance in Google Sheet.",
            )

        return {
            "status": "success",
            "message": f"Successfully checked in {updated_student['full_name']}!",
            **updated_student
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred: {str(exc)}",
        )


@app.get(
    "/api/attendance/stats",
    response_model=StatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Attendance Statistics",
    description="Returns check-in counts (total registered vs present) after verifying Coordinator PIN.",
)
async def get_stats(pin: str) -> Dict[str, Any]:
    """
    Returns check-in stats.
    """
    if pin != COORDINATOR_PIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid coordinator PIN code.",
        )

    try:
        total, present = sheets_service.get_attendance_stats()
        return {
            "status": "success",
            "total_registrations": total,
            "checked_in_count": present,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred: {str(exc)}",
        )


ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

@app.post(
    "/api/admin/process-tickets",
    response_model=AdminProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Process Pending Approvals & Rejections",
    description="Reads Google Sheet, sends QR tickets to 'Approved' students and rejection emails to 'Rejected' students.",
)
async def process_tickets(request: AdminProcessRequest) -> Dict[str, Any]:
    """
    Handles processing tickets.
    """
    if request.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin password.",
        )

    try:
        students = sheets_service.get_all_registrations()
        approved_sent = 0
        rejected_sent = 0
        
        for student in students:
            status_val = student.get("status", "").strip().lower()
            if status_val == "approved":
                try:
                    await send_ticket_email(student["email"], student["full_name"], student["registration_id"])
                    sheets_service.update_student_status(student["worksheet_title"], student["row_idx"], "Ticket Sent")
                    approved_sent += 1
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(f"Failed to send ticket to {student['email']}: {e}")
            elif status_val == "rejected":
                try:
                    await send_rejection_email(student["email"], student["full_name"])
                    sheets_service.update_student_status(student["worksheet_title"], student["row_idx"], "Rejection Sent")
                    rejected_sent += 1
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(f"Failed to send rejection to {student['email']}: {e}")

        return {
            "status": "success",
            "approved_sent": approved_sent,
            "rejected_sent": rejected_sent,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing tickets: {str(exc)}",
        )



if __name__ == "__main__":
    import uvicorn

    uvicorn.run("index:app", host="0.0.0.0", port=8000, reload=True)
