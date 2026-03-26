from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


# 👤 USER
class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime


# 🧾 REPORT
class ReportUpload(BaseModel):
    user_id: str


class ReportResponse(BaseModel):
    id: str
    user_id: str

    file_id: str   # GridFS file reference

    status: str

    raw_text: Optional[str] = None
    ai_data: Optional[Dict] = None

    created_at: datetime
    updated_at: Optional[datetime] = None



# 💊 PRESCRIPTION
class PrescriptionUpload(BaseModel):
    user_id: str


class PrescriptionResponse(BaseModel):
    id: str
    user_id: str

    file_id: str   # GridFS file reference

    status: str

    raw_text: Optional[str] = None
    ai_data: Optional[Dict] = None

    created_at: datetime
    updated_at: Optional[datetime] = None


# 🤖 AI OUTPUT
class AIData(BaseModel):
    summary: Optional[str]
    key_data: Optional[Dict]


# 📜 HISTORY
class HistoryResponse(BaseModel):
    reports: List[ReportResponse]
    prescriptions: List[PrescriptionResponse]