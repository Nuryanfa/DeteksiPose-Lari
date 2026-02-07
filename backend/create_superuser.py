import sys
import os

# Create/Ensure backend directory is in path
sys.path.append(os.getcwd())

from app.db.session import SessionLocal, engine, Base
from app.crud import crud_user
from app.schemas.user import UserCreate
from app.models.user import User, UserRole

def init():
    # ENSURE TABLES EXIST
    print("Checking database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    email = "admin@ssts.com"
    password = "admin"
    
    print(f"Checking for user: {email}")
    user = crud_user.get_by_email(db, email=email)
    if not user:
        print("Creating new superuser...")
        user_in = UserCreate(
            email=email,
            password=password,
            full_name="Administrator",
            role=UserRole.ADMIN
        )
        try:
            user = crud_user.create(db, obj_in=user_in)
            print(f"============================================")
            print(f"SUPERUSER CREATED SUCCESSFULLY")
            print(f"Email    : {email}")
            print(f"Password : {password}")
            print(f"============================================")
        except Exception as e:
            print(f"Error creating user: {e}")
    else:
        print(f"Superuser {email} already exists.")

if __name__ == "__main__":
    init()
