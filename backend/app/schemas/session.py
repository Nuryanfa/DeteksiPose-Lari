from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SessionBase(BaseModel):
    duration_seconds: float = 0.0
    technique_score: float = 0.0
    avg_cadence: float = 0.0
    avg_stride_length: float = 0.0
    avg_gct: float = 0.0
    max_swing_error: float = 0.0
    max_hip_error: float = 0.0
    video_path: Optional[str] = None
    coach_notes: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class SessionFeedbackUpdate(BaseModel):
    coach_notes: str

class Session(SessionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
