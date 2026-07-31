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
        if not self.credentials_json:
            raise ValueError(
                "GOOGLE_SERVICE_ACCOUNT_JSON environment variable is not configured. "
                "Provide a valid file path or raw JSON string."
            )

        target_path = self.credentials_json
        if not os.path.isfile(target_path):
            api_dir = os.path.dirname(os.path.abspath(__file__))
            alt_path = os.path.join(api_dir, self.credentials_json)
            if os.path.isfile(alt_path):
                target_path = alt_path

        if os.path.isfile(target_path):
            return Credentials.from_service_account_file(target_path, scopes=SCOPES)

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
        # Select first worksheet by index (0) so name doesn't matter
        self.worksheet = self.sheet.get_worksheet(0)
        self._ensure_headers()
        return self.worksheet

    def _ensure_headers(self) -> None:
        """
        Ensures the header row exists in the worksheet and matches the required schema.
        """
        if self.worksheet is None:
            return
        
        expected_headers = [
            "Timestamp",
            "Full Name",
            "Enrollment No",
            "Email",
            "Phone Number",
            "Class",
            "Has Mac",
            "Registration ID",
            "Attendance",
            "Status"
        ]
        existing_headers = self.worksheet.row_values(1)
        if not existing_headers:
            self.worksheet.append_row(expected_headers)
        elif len(existing_headers) < len(expected_headers):
            # Pad the worksheet headers with missing columns
            for i, header in enumerate(expected_headers):
                if i >= len(existing_headers):
                    self.worksheet.update_cell(1, i + 1, header)

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
        phone_number: str,
        class_name: str,
        has_mac: str,
        registration_id: str,
        attendance: str = "Absent",
        status: str = "Pending"
    ) -> List[str]:
        """
        Appends a new student registration record to the Google Sheet.
        Row format: [Timestamp, Full Name, Enrollment No, Email, Phone Number, Class, Has Mac, Registration ID, Attendance, Status]
        """
        worksheet = self.connect()
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        row = [
            timestamp,
            full_name.strip(),
            str(enrollment_no).strip(),
            email.strip(),
            phone_number.strip(),
            class_name.strip(),
            has_mac.strip(),
            registration_id.strip(),
            attendance.strip(),
            status.strip(),
        ]
        worksheet.append_row(row)
        return row

    def get_student_by_registration_id(self, registration_id: str) -> Optional[Tuple[int, dict]]:
        """
        Searches the Google Sheet for a registration_id (Column 8) or Enrollment No (Column 3).
        Returns a tuple of (row_index, student_data_dict) if found, else None.
        """
        worksheet = self.connect()
        all_values = worksheet.get_all_values()
        if len(all_values) <= 1:
            return None
        
        clean_target = str(registration_id).strip().lower()
        if not clean_target:
            return None

        for idx, row in enumerate(all_values[1:], start=2):
            # Check Registration ID (index 8) or Enrollment No (index 3)
            match_registration = len(row) >= 8 and str(row[7]).strip().lower() == clean_target
            match_enrollment = len(row) >= 3 and str(row[2]).strip().lower() == clean_target

            if match_registration or match_enrollment:
                student = {
                    "full_name": row[1] if len(row) >= 2 else "",
                    "enrollment_no": row[2] if len(row) >= 3 else "",
                    "email": row[3] if len(row) >= 4 else "",
                    "phone_number": row[4] if len(row) >= 5 else "",
                    "class_name": row[5] if len(row) >= 6 else "",
                    "has_mac": row[6] if len(row) >= 7 else "",
                    "registration_id": row[7] if len(row) >= 8 else "",
                    "attendance": row[8] if len(row) >= 9 else "Absent",
                    "status": row[9] if len(row) >= 10 else "Pending",
                    "row_idx": idx
                }
                return idx, student
        return None

    def mark_attendance(self, registration_id: str, status: str = "Present") -> Optional[dict]:
        """
        Finds student by registration_id and updates their attendance status in column 9.
        Returns the updated student dictionary or None if not found.
        """
        worksheet = self.connect()
        result = self.get_student_by_registration_id(registration_id)
        if not result:
            return None
        
        row_idx, student = result
        # Update cell in column 9 (Attendance)
        worksheet.update_cell(row_idx, 9, status)
        student["attendance"] = status
        return student

    def get_all_registrations(self) -> List[dict]:
        """
        Returns a list of all registrations with their row index.
        """
        worksheet = self.connect()
        all_values = worksheet.get_all_values()
        if len(all_values) <= 1:
            return []
        
        students = []
        for idx, row in enumerate(all_values[1:], start=2):
            students.append({
                "row_idx": idx,
                "full_name": row[1] if len(row) >= 2 else "",
                "enrollment_no": row[2] if len(row) >= 3 else "",
                "email": row[3] if len(row) >= 4 else "",
                "phone_number": row[4] if len(row) >= 5 else "",
                "class_name": row[5] if len(row) >= 6 else "",
                "has_mac": row[6] if len(row) >= 7 else "",
                "registration_id": row[7] if len(row) >= 8 else "",
                "attendance": row[8] if len(row) >= 9 else "Absent",
                "status": row[9] if len(row) >= 10 else "Pending"
            })
        return students

    def update_student_status(self, row_idx: int, new_status: str) -> None:
        """
        Updates the status in column 10 for a specific row index.
        """
        worksheet = self.connect()
        worksheet.update_cell(row_idx, 10, new_status)

    def get_attendance_stats(self) -> Tuple[int, int]:
        """
        Calculates stats of checked-in vs total registrations.
        Returns a tuple of (total_registrations, checked_in_count).
        """
        worksheet = self.connect()
        all_values = worksheet.get_all_values()
        if len(all_values) <= 1:
            return 0, 0
        
        total = len(all_values) - 1
        present = 0
        for row in all_values[1:]:
            if len(row) >= 9 and str(row[8]).strip().lower() == "present":
                present += 1
        return total, present

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
