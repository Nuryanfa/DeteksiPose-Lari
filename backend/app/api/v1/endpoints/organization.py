from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Any
from app.api import deps
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.session import AnalysisSession
from datetime import datetime, date

router = APIRouter()

@router.get("/summary")
def get_organization_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get high-level statistics for the organization (Management only).
    """
    if current_user.role != UserRole.MANAGEMENT and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 1. Total Athletes
    total_athletes = db.query(User).filter(User.role == UserRole.ATHLETE).count()

    # 2. Total Sessions
    total_sessions = db.query(AnalysisSession).count()

    # 3. Average Technique Score (System-wide)
    avg_score = db.query(func.avg(AnalysisSession.technique_score)).scalar() or 0

    # 4. Active Today
    today = date.today()
    active_today = db.query(AnalysisSession).filter(func.date(AnalysisSession.created_at) == today).distinct(AnalysisSession.user_id).count()

    return {
        "total_athletes": total_athletes,
        "total_sessions": total_sessions,
        "avg_system_score": round(avg_score, 1),
        "active_today": active_today
    }

@router.get("/recent-sessions")
def get_all_recent_sessions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get recent sessions from ALL users (Management only).
    """
    if current_user.role not in [UserRole.MANAGEMENT, UserRole.ADMIN, UserRole.COACH]:
        raise HTTPException(status_code=403, detail="Not authorized")

    sessions = (
        db.query(AnalysisSession, User.full_name)
        .join(User, AnalysisSession.user_id == User.id)
        .order_by(AnalysisSession.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Format response
    result = []
    for session, athlete_name in sessions:
        sess_dict = {
            "id": session.id,
            "created_at": session.created_at,
            "technique_score": session.technique_score,
            "duration_seconds": session.duration_seconds,
            "athlete_name": athlete_name,
            "athlete_id": session.user_id
        }
        result.append(sess_dict)

    return result
