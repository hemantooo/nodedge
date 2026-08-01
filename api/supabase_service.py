import os
from typing import List, Optional, Tuple, Dict, Any
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseService:
    """
    Service class to handle operations with Supabase.
    """
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        url: str = supabase_url or os.environ.get("SUPABASE_URL", "")
        key: str = supabase_key or os.environ.get("SUPABASE_KEY", "")
        
        self.client: Optional[Client] = None
        if url and key:
            opts = ClientOptions(persist_session=False)
            self.client = create_client(url, key, options=opts)

    def is_enrollment_registered(self, enrollment_no: str) -> bool:
        """
        Checks if an enrollment number already exists in the Supabase table.
        """
        if not self.client:
            raise ValueError("Supabase client is not initialized.")
            
        clean_target = str(enrollment_no).strip().lower()
        response = self.client.table("registrations").select("id").ilike("enrollment_no", clean_target).execute()
        return len(response.data) > 0

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
        if not self.client:
            raise ValueError("Supabase client is not initialized.")
            
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
        response = self.client.table("registrations").insert(data).execute()
        return response.data[0] if response.data else {}

    def get_student_by_registration_id(self, registration_id: str) -> Optional[Tuple[None, dict]]:
        """
        Searches Supabase for a registration_id or Enrollment No.
        Returns a tuple of (None, student_data_dict) if found, else None.
        (None is returned for row_idx to keep backward compatibility with index.py destructing).
        """
        if not self.client:
            return None
            
        clean_target = str(registration_id).strip().lower()
        if not clean_target:
            return None

        response = self.client.table("registrations").select("*").or_(f"registration_id.ilike.%{clean_target}%,enrollment_no.ilike.%{clean_target}%").execute()
        
        if response.data and len(response.data) > 0:
            return None, response.data[0]
            
        return None

    def mark_attendance(self, registration_id: str, status: str = "Present") -> Optional[dict]:
        """
        Finds student by registration_id and updates their attendance status.
        """
        if not self.client:
            return None
            
        result = self.get_student_by_registration_id(registration_id)
        if not result:
            return None
            
        _, student = result
        response = self.client.table("registrations").update({"attendance": status}).eq("id", student["id"]).execute()
        
        if response.data:
            return response.data[0]
        return None

    def get_all_registrations(self) -> List[dict]:
        """
        Returns a list of all registrations.
        """
        if not self.client:
            return []
            
        response = self.client.table("registrations").select("*").execute()
        return response.data

    def update_student_status(self, student_uuid: str, new_status: str) -> None:
        """
        Updates the status for a specific student UUID.
        """
        if not self.client:
            return
            
        self.client.table("registrations").update({"status": new_status}).eq("id", student_uuid).execute()

    def get_attendance_stats(self) -> Tuple[int, int]:
        """
        Calculates stats of checked-in vs total registrations.
        """
        if not self.client:
            return 0, 0
            
        total_res = self.client.table("registrations").select("id", count="exact").execute()
        total = total_res.count if total_res.count is not None else 0
        
        present_res = self.client.table("registrations").select("id", count="exact").ilike("attendance", "present").execute()
        present = present_res.count if present_res.count is not None else 0
        
        return total, present

    def get_total_registrations(self) -> int:
        """
        Returns total count of registered students.
        """
        if not self.client:
            return 0
            
        total_res = self.client.table("registrations").select("id", count="exact").execute()
        return total_res.count if total_res.count is not None else 0

    def check_health(self) -> Tuple[bool, int, Optional[str]]:
        """
        Checks Supabase connection health and registration count.
        Returns: (is_connected, total_count, error_message)
        """
        try:
            if not self.client:
                return False, 0, "Supabase client not initialized (check URL and Key)."
            count = self.get_total_registrations()
            return True, count, None
        except Exception as e:
            return False, 0, str(e)


# Global default instance for application usage
supabase_service = SupabaseService()
