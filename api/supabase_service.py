import os
import json
import ssl
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Optional, Tuple, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a lightweight unverified SSL context to prevent disk CA cert bundle locks in Vercel sandbox
SSL_CONTEXT = ssl._create_unverified_context()

class SupabaseService:
    """
    Service class to handle operations with Supabase using native REST API.
    Bypasses third-party SDK dependencies for maximum stability on Vercel Serverless.
    """
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        raw_url = (supabase_url or os.environ.get("SUPABASE_URL", "")).strip().strip('"').strip("'")
        self.url: str = raw_url.rstrip("/")
        raw_key = (supabase_key or os.environ.get("SUPABASE_KEY", "")).strip().strip('"').strip("'")
        self.key: str = raw_key

    def _request(self, method: str, endpoint: str, data: Optional[dict] = None, headers_extra: Optional[dict] = None) -> Any:
        if not self.url or not self.key:
            raise ValueError("Supabase URL or Key is not configured.")

        full_url = f"{self.url}/rest/v1/{endpoint}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        if headers_extra:
            headers.update(headers_extra)

        body_bytes = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(full_url, data=body_bytes, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, context=SSL_CONTEXT) as resp:
                res_body = resp.read().decode("utf-8")
                return json.loads(res_body) if res_body else []
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            raise RuntimeError(f"Supabase API Error ({e.code}): {err_body}")
        except Exception as e:
            raise RuntimeError(f"Supabase Request Failed: {str(e)}")

    def is_enrollment_registered(self, enrollment_no: str) -> bool:
        """
        Checks if an enrollment number already exists in the Supabase table.
        """
        clean_target = urllib.parse.quote(str(enrollment_no).strip().lower())
        endpoint = f"registrations?select=id&enrollment_no=ilike.{clean_target}"
        res = self._request("GET", endpoint)
        return isinstance(res, list) and len(res) > 0

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
    ) -> dict:
        """
        Appends a new student registration record to Supabase.
        """
        data = {
            "full_name": full_name.strip(),
            "enrollment_no": str(enrollment_no).strip(),
            "email": email.strip(),
            "phone_number": phone_number.strip(),
            "class_name": class_name.strip(),
            "has_mac": has_mac.strip(),
            "registration_id": registration_id.strip(),
            "attendance": attendance.strip(),
            "status": status.strip(),
        }
        res = self._request("POST", "registrations", data=data)
        if isinstance(res, list) and len(res) > 0:
            return res[0]
        return res if isinstance(res, dict) else {}

    def get_student_by_registration_id(self, registration_id: str) -> Optional[Tuple[None, dict]]:
        """
        Searches Supabase for a registration_id or Enrollment No.
        Returns a tuple of (None, student_data_dict) if found, else None.
        """
        clean_target = urllib.parse.quote(str(registration_id).strip().lower())
        if not clean_target:
            return None

        endpoint = f"registrations?select=*&or=(registration_id.ilike.%25{clean_target}%25,enrollment_no.ilike.%25{clean_target}%25)"
        res = self._request("GET", endpoint)
        if isinstance(res, list) and len(res) > 0:
            return None, res[0]
        return None

    def mark_attendance(self, registration_id: str, status: str = "Present") -> Optional[dict]:
        """
        Finds student by registration_id and updates their attendance status.
        """
        result = self.get_student_by_registration_id(registration_id)
        if not result:
            return None
            
        _, student = result
        student_id = student["id"]
        endpoint = f"registrations?id=eq.{student_id}"
        res = self._request("PATCH", endpoint, data={"attendance": status})
        if isinstance(res, list) and len(res) > 0:
            return res[0]
        return None

    def get_all_registrations(self) -> List[dict]:
        """
        Returns a list of all registrations.
        """
        res = self._request("GET", "registrations?select=*")
        return res if isinstance(res, list) else []

    def update_student_status(self, student_uuid: str, new_status: str) -> None:
        """
        Updates the status for a specific student UUID.
        """
        endpoint = f"registrations?id=eq.{student_uuid}"
        self._request("PATCH", endpoint, data={"status": new_status})

    def get_attendance_stats(self) -> Tuple[int, int]:
        """
        Calculates stats of checked-in vs total registrations.
        """
        try:
            all_regs = self.get_all_registrations()
            total = len(all_regs)
            present = sum(1 for r in all_regs if str(r.get("attendance", "")).lower() == "present")
            return total, present
        except Exception:
            return 0, 0

    def get_total_registrations(self) -> int:
        """
        Returns total count of registered students.
        """
        total, _ = self.get_attendance_stats()
        return total

    def check_health(self) -> Tuple[bool, int, Optional[str]]:
        """
        Checks Supabase connection health and registration count.
        """
        try:
            if not self.url or not self.key:
                return False, 0, "Supabase URL or Key not configured."
            total = self.get_total_registrations()
            return True, total, None
        except Exception as e:
            return False, 0, str(e)


# Global default instance for application usage
supabase_service = SupabaseService()
