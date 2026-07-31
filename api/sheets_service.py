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

    def _get_credentials(self) -> Credentials:
        if not self.credentials_json:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable is not configured.")
        
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
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON must be either a valid file path or a valid JSON string.") from err

    def connect(self) -> None:
        if self.sheet is not None:
            return

        if not self.spreadsheet_id:
            raise ValueError("GOOGLE_SHEETS_SPREADSHEET_ID environment variable is missing.")

        creds = self._get_credentials()
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(self.spreadsheet_id)

    def get_worksheet(self, has_mac: str) -> gspread.Worksheet:
        self.connect()
        title = "Mac Students" if has_mac.strip().lower() == "yes" else "Non-Mac Students"
        try:
            worksheet = self.sheet.worksheet(title)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = self.sheet.add_worksheet(title=title, rows="1000", cols="20")
        self._ensure_headers(worksheet)
        return worksheet
        
    def _get_all_worksheets(self) -> List[gspread.Worksheet]:
        self.connect()
        titles = ["Mac Students", "Non-Mac Students"]
        worksheets = []
        for t in titles:
            try:
                worksheets.append(self.sheet.worksheet(t))
            except gspread.exceptions.WorksheetNotFound:
                pass
        return worksheets

    def _ensure_headers(self, worksheet: gspread.Worksheet) -> None:
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
        existing_headers = worksheet.row_values(1)
        if not existing_headers:
            worksheet.append_row(expected_headers)
        elif len(existing_headers) < len(expected_headers):
            for i, header in enumerate(expected_headers):
                if i >= len(existing_headers):
                    worksheet.update_cell(1, i + 1, header)

    def is_enrollment_registered(self, enrollment_no: str) -> bool:
        clean_target = str(enrollment_no).strip().lower()
        for worksheet in self._get_all_worksheets():
            enrollment_col = worksheet.col_values(3)
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
        worksheet = self.get_worksheet(has_mac)
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

    def get_student_by_registration_id(self, registration_id: str) -> Optional[Tuple[gspread.Worksheet, int, dict]]:
        clean_target = str(registration_id).strip().lower()
        if not clean_target:
            return None

        for worksheet in self._get_all_worksheets():
            all_values = worksheet.get_all_values()
            if len(all_values) <= 1:
                continue

            for idx, row in enumerate(all_values[1:], start=2):
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
                        "worksheet_title": worksheet.title,
                        "row_idx": idx
                    }
                    return worksheet, idx, student
        return None

    def mark_attendance(self, registration_id: str, status: str = "Present") -> Optional[dict]:
        result = self.get_student_by_registration_id(registration_id)
        if not result:
            return None
        
        worksheet, row_idx, student = result
        worksheet.update_cell(row_idx, 9, status)
        student["attendance"] = status
        return student

    def get_all_registrations(self) -> List[dict]:
        students = []
        for worksheet in self._get_all_worksheets():
            all_values = worksheet.get_all_values()
            if len(all_values) <= 1:
                continue
            
            for idx, row in enumerate(all_values[1:], start=2):
                students.append({
                    "worksheet_title": worksheet.title,
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

    def update_student_status(self, worksheet_title: str, row_idx: int, new_status: str) -> None:
        self.connect()
        worksheet = self.sheet.worksheet(worksheet_title)
        worksheet.update_cell(row_idx, 10, new_status)

    def get_attendance_stats(self) -> Tuple[int, int]:
        total = 0
        present = 0
        for worksheet in self._get_all_worksheets():
            all_values = worksheet.get_all_values()
            if len(all_values) > 1:
                total += len(all_values) - 1
                for row in all_values[1:]:
                    if len(row) >= 9 and str(row[8]).strip().lower() == "present":
                        present += 1
        return total, present

    def get_total_registrations(self) -> int:
        total = 0
        for worksheet in self._get_all_worksheets():
            all_values = worksheet.get_all_values()
            if all_values:
                total += max(0, len(all_values) - 1)
        return total

    def check_health(self) -> Tuple[bool, int, Optional[str]]:
        try:
            count = self.get_total_registrations()
            return True, count, None
        except Exception as e:
            return False, 0, str(e)


# Global default instance for application usage
sheets_service = GoogleSheetsService()
