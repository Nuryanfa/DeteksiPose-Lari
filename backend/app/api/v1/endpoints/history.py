from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.db.session import get_db
from app.models.session import AnalysisSession
from app.models.user import User
from app.schemas.session import SessionCreate, Session as SessionSchema, SessionFeedbackUpdate

router = APIRouter()

@router.post("/save", response_model=SessionSchema)
def save_session(
    *,
    db: Session = Depends(get_db),
    session_in: SessionCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Save a new analysis session.
    """
    session = AnalysisSession(
        user_id=current_user.id,
        duration_seconds=session_in.duration_seconds,
        technique_score=session_in.technique_score,
        avg_cadence=session_in.avg_cadence,
        avg_stride_length=session_in.avg_stride_length,
        avg_gct=session_in.avg_gct,
        max_swing_error=session_in.max_swing_error,
        max_hip_error=session_in.max_hip_error,
        video_path=session_in.video_path
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/", response_model=List[SessionSchema])
def read_sessions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: int = None, # Optional: View specific user's history
    current_user: User = Depends(deps.get_current_user)
):
    """
    Retrieve sessions. 
    - Athletes: Only see own sessions.
    - Coach/Management: Can see own or specific athlete's sessions (via user_id param).
    """
    from app.models.user import UserRole

    target_user_id = current_user.id
    
    # If a specific user_id is requested
    if user_id:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGEMENT, UserRole.COACH]:
             raise HTTPException(status_code=403, detail="Not authorized to view other users' data")
        target_user_id = user_id

    sessions = db.query(AnalysisSession).filter(AnalysisSession.user_id == target_user_id).order_by(AnalysisSession.created_at.desc()).offset(skip).limit(limit).all()
    return sessions

@router.put("/{session_id}/feedback", response_model=SessionSchema)
def update_session_feedback(
    *,
    db: Session = Depends(get_db),
    session_id: int,
    feedback_in: SessionFeedbackUpdate, 
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update session feedback (Coach only).
    """
    from app.models.user import UserRole
    # SessionFeedbackUpdate is already imported
    
    if current_user.role != UserRole.COACH:
         raise HTTPException(status_code=403, detail="Only coaches can provide feedback")

    session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.coach_notes = feedback_in.coach_notes
    db.commit()
    db.refresh(session)
    return session
