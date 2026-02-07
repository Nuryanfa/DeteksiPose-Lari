import logging
from app.db.session import SessionLocal
from app.crud import crud_user
from app.schemas.user import UserCreate
from app.models.user import UserRole
from app.models.session import AnalysisSession  # Fix for mapper error
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_dummy_users():
    db = SessionLocal()
    
    dummy_users = [
        {
            "email": "koni@ssts.com",
            "password": "konipassword",
            "full_name": "KONI Management",
            "role": UserRole.MANAGEMENT
        },
        {
            "email": "coach@ssts.com",
            "password": "coachpassword",
            "full_name": "Coach Budi",
            "role": UserRole.COACH
        },
        {
            "email": "atlet@ssts.com",
            "password": "atletpassword",
            "full_name": "Atlet Juara",
            "role": UserRole.ATHLETE
        }
    ]

    for user_data in dummy_users:
        user = crud_user.get_by_email(db, email=user_data["email"])
        if not user:
            user_in = UserCreate(
                email=user_data["email"],
                password=user_data["password"],
                full_name=user_data["full_name"],
                role=user_data["role"]
            )
            crud_user.create(db, obj_in=user_in)
            logger.info(f"User created: {user_data['email']} ({user_data['role']})")
        else:
            logger.info(f"User already exists: {user_data['email']}")

    db.close()

if __name__ == "__main__":
    logger.info("Creating dummy users...")
    init_dummy_users()
    logger.info("Dummy users created successfully.")
