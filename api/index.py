"""
Main FastAPI Application Entry Point for Workshop Registration Backend Server.
Handles CORS, validation, duplicate prevention, registration submission, and health checks.
"""

import hashlib
import time
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, status, BackgroundTasks
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.schemas import HealthResponse, RegistrationRequest, RegistrationResponse
from api.sheets_service import sheets_service
from api.email_service import send_ticket_email

# Initialize FastAPI application
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

    # 2. Append new row to Google Sheet
    try:
        sheets_service.append_registration(
            full_name=request.full_name,
            enrollment_no=request.enrollment_no,
            email=request.email,
            semester=request.semester,
            has_mac=request.has_mac,
            proficiency=request.proficiency,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to append registration data to Google Sheet: {str(exc)}",
        )

    # 3. Generate unique registration hash ID
    registration_id = generate_registration_id(request.enrollment_no)

    # Queue ticket email in the background
    background_tasks.add_task(send_ticket_email, request.email, request.full_name, registration_id)

    # 4. Return success response
    return {
        "status": "success",
        "message": "Registration successful!",
        "registration_id": registration_id,
    }


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
