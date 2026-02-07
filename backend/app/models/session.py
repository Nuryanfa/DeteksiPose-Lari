from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from datetime import datetime

class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Metrics
    duration_seconds = Column(Float, default=0.0)
    technique_score = Column(Float, default=0.0)
    avg_cadence = Column(Float, default=0.0)
    avg_stride_length = Column(Float, default=0.0)
    avg_gct = Column(Float, default=0.0)
    
    # Error Counts (Saved as simple Integers/Strings or JSON strings if needed. Simple columns are easier for MVP)
    max_swing_error = Column(Float, default=0.0)
    max_hip_error = Column(Float, default=0.0)
    
    # File Path (Optional, for replay)
    video_path = Column(String, nullable=True)

    # Feedback
    coach_notes = Column(String, nullable=True)

    owner = relationship("User", back_populates="sessions")
