
import sys
import os

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.app.db.session import SessionLocal
from backend.app.models.session import AnalysisSession
from backend.app.models.user import User

def debug_save():
    print("Debug: Connecting to DB...")
    db = SessionLocal()
    try:
        # Get first user
        user = db.query(User).first()
        if not user:
            print("No user found!")
            return

        print(f"Found user: {user.email} (ID: {user.id})")
        
        # Try creating session
        print("Attempting to save session...")
        session = AnalysisSession(
            user_id=user.id,
            duration_seconds=10.0,
            technique_score=80.0,
            avg_cadence=150.0,
            avg_stride_length=1.0,
            avg_gct=200.0,
            max_swing_error=10.0,
            max_hip_error=5.0,
            video_path="debug_video.mp4"
            # coach_notes is None by default
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        print(f"✅ SUCCESS: Session saved with ID {session.id}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_save()
