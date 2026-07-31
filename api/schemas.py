"""
Pydantic data models and schemas for workshop registration.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class RegistrationRequest(BaseModel):
    """
    Data validation schema for student workshop registration submissions.
    """
    full_name: str = Field(..., min_length=1, description="Student's full name", example="John Doe")
    enrollment_no: str = Field(..., min_length=1, description="Student's unique enrollment number", example="210303123001")
    email: EmailStr = Field(..., description="Student's institutional email address", example="john.doe@paruluniversity.ac.in")
    class_name: str = Field(..., min_length=1, description="Current class (e.g., 2AIML4)", example="2AIML4")
    phone_number: str = Field(..., min_length=10, max_length=10, pattern=r'^\d{10}$', description="10-digit phone number without country code", example="9876543210")
    has_mac: str = Field(..., description="Does the student have a Mac device? ('yes' or 'no')", example="yes")

    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v: EmailStr) -> EmailStr:
        """
        Validates that the email address belongs to the @paruluniversity.ac.in domain.
        """
        email_str = str(v).lower()
        allowed_domain = "@paruluniversity.ac.in"
        if not email_str.endswith(allowed_domain):
            raise ValueError(f"Email must end with {allowed_domain}")
        return v


class RegistrationResponse(BaseModel):
    """
    Response schema returned upon successful registration.
    """
    status: str = Field(default="success", description="Status of the operation")
    message: str = Field(default="Registration successful!", description="User friendly response message")
    registration_id: str = Field(..., description="Unique generated hash/ID for the registration submission")


class HealthResponse(BaseModel):
    """
    Response schema for health status check endpoint.
    """
    status: str = Field(..., description="Health status of backend service")
    total_registrations: int = Field(..., description="Total count of registrations in Google Sheet")
    google_sheets_connected: bool = Field(..., description="Status of Google Sheets API connectivity")
    message: Optional[str] = Field(None, description="Additional status message if disconnected")


class AttendanceRequest(BaseModel):
    """
    Schema for marking attendance.
    """
    registration_id: str = Field(..., description="Unique registration ID from QR code")
    pin: str = Field(..., description="Coordinator security PIN")


class AttendanceResponse(BaseModel):
    """
    Schema for attendance response.
    """
    status: str = Field(..., description="Status of check-in ('success', 'already_marked', 'error')")
    message: str = Field(..., description="Details of check-in result")
    full_name: Optional[str] = Field(None, description="Student's full name")
    enrollment_no: Optional[str] = Field(None, description="Student's enrollment number")
    email: Optional[str] = Field(None, description="Student's email")
    class_name: Optional[str] = Field(None, description="Student's class")
    phone_number: Optional[str] = Field(None, description="Student's phone number")
    has_mac: Optional[str] = Field(None, description="Student's Mac availability status")
    attendance: Optional[str] = Field(None, description="Attendance status")


class StatsResponse(BaseModel):
    """
    Response schema for check-in statistics.
    """
    status: str = Field("success")
    total_registrations: int = Field(..., description="Total registrations count")
    checked_in_count: int = Field(..., description="Total checked-in (present) count")


class AdminProcessRequest(BaseModel):
    """
    Schema for processing tickets in the admin dashboard.
    """
    password: str = Field(..., description="Admin password to process tickets")


class AdminProcessResponse(BaseModel):
    """
    Response schema for processing tickets.
    """
    status: str = Field(default="success")
    approved_sent: int = Field(..., description="Number of approved tickets sent")
    rejected_sent: int = Field(..., description="Number of rejection emails sent")
