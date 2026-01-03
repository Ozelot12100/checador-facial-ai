from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Employee DTOs ---
class EmployeeBase(BaseModel):
    code: str
    full_name: str
    face_vector: List[float] # Recibe una lista de doubles/floats

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: str
    is_active: bool
    created_at_utc: datetime
    photo_path: Optional[str] = None

    class Config:
        from_attributes = True # Permite leer datos desde los modelos de SQLAlchemy

# --- Attendance DTOs ---
class CheckInRequest(BaseModel):
    face_vector: List[float]
    device_info: Optional[str] = ""

class CheckInResponse(BaseModel):
    success: bool
    message: str
    employee_name: Optional[str] = None
    employee_code: Optional[str] = None
    time: str

class AttendanceRecordResponse(BaseModel):
    id: str
    timestamp_utc: datetime
    type: int # 0 o 1
    match_score: float
    employee_id: str
    employee_name: str
    employee_code: str
    photo_path: Optional[str] = None

    class Config:
        from_attributes = True