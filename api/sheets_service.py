"""
Google Sheets integration helper using gspread and google-auth.
Supports service account authentication via file path or raw JSON string.
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Tuple
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define Google API scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


class GoogleSheetsService:
    """
    Service class to handle operations with Google Sheets API.
    """

    def __init__(self, spreadsheet_id: Optional[str] = None, credentials_json: Optional[str] = None):
        self.spreadsheet_id = spreadsheet_id or os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
        self.credentials_json = credentials_json or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        self.client: Optional[gspread.Client] = None
        self.sheet: Optional[gspread.Spreadsheet] = None
        self.worksheet: Optional[gspread.Worksheet] = None

    def _get_credentials(self) -> Credentials:
        """
        Parses credentials from file path or raw JSON string.
        """
        if not self.credentials_json:
            raise ValueError(
                "GOOGLE_SERVICE_ACCOUNT_JSON environment variable is not configured. "
                "Provide a valid file path or raw JSON string."
            )

        # Check if credentials_json is a path to an existing file
        if os.path.isfile(self.credentials_json):
            return Credentials.from_service_account_file(self.credentials_json, scopes=SCOPES)

        # Try parsing as raw JSON string
        try:
            cred_dict = json.loads(self.credentials_json)
            return Credentials.from_service_account_info(cred_dict, scopes=SCOPES)
        except json.JSONDecodeError as err:
            raise ValueError(
                "GOOGLE_SERVICE_ACCOUNT_JSON must be either a valid file path or a valid JSON string."
            ) from err

    def connect(self) -> gspread.Worksheet:
        """
        Establishes connection to Google Sheets client and opens the target worksheet.
        """
        if self.worksheet is not None:
            return self.worksheet

        if not self.spreadsheet_id:
            raise ValueError(
                "GOOGLE_SHEETS_SPREADSHEET_ID environment variable is missing. "
                "Set it to your Google Sheet ID."
            )

        creds = self._get_credentials()
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(self.spreadsheet_id)
        # Select first worksheet by default
        self.worksheet = self.sheet.sheet1
        self._ensure_headers()
        return self.worksheet

    def _ensure_headers(self) -> None:
        """
        Ensures the header row exists in the worksheet.
        """
        if self.worksheet is None:
            return
        
        expected_headers = [
            "Timestamp",
            "Full Name",
            "Enrollment No",
            "Email",
            "Semester",
            "Has Mac",
            "Proficiency"
        ]
        existing_headers = self.worksheet.row_values(1)
        if not existing_headers:
            self.worksheet.append_row(expected_headers)

    def is_enrollment_registered(self, enrollment_no: str) -> bool:
        """
        Checks if an enrollment number already exists in the Google Sheet.
        Column 3 represents Enrollment No.
        """
        worksheet = self.connect()
        # Fetch all values in Column 3 (Enrollment No)
        enrollment_col = worksheet.col_values(3)
        clean_target = str(enrollment_no).strip().lower()
        
        # Skip header if present
        for val in enrollment_col[1:]:
            if str(val).strip().lower() == clean_target:
                return True
        return False

    def append_registration(
        self,
        full_name: str,
        enrollment_no: str,
        email: str,
        semester: str,
        has_mac: str,
        proficiency: str,
    ) -> List[str]:
        """
        Appends a new student registration record to the Google Sheet.
        Row format: [Timestamp, Full Name, Enrollment No, Email, Semester, Has Mac, Proficiency]
        """
        worksheet = self.connect()
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        row = [
            timestamp,
            full_name.strip(),
            str(enrollment_no).strip(),
            email.strip(),
            semester.strip(),
            has_mac.strip(),
            proficiency.strip(),
        ]
        worksheet.append_row(row)
        return row

    def get_total_registrations(self) -> int:
        """
        Returns total count of registered students in the Google Sheet (excluding header).
        """
        worksheet = self.connect()
        all_values = worksheet.get_all_values()
        if not all_values:
            return 0
        # If headers exist, subtract header row count
        return max(0, len(all_values) - 1)

    def check_health(self) -> Tuple[bool, int, Optional[str]]:
        """
        Checks Google Sheets API connection health and registration count.
        Returns: (is_connected, total_count, error_message)
        """
        try:
            count = self.get_total_registrations()
            return True, count, None
        except Exception as e:
            return False, 0, str(e)


# Global default instance for application usage
sheets_service = GoogleSheetsService()
