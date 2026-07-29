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
    semester: str = Field(..., min_length=1, description="Current semester", example="Semester 5")
    proficiency: str = Field(..., min_length=1, description="Skill/Proficiency level", example="Intermediate")
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
