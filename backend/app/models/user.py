from sqlalchemy import Boolean, Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    COACH = "coach"
    ATHLETE = "athlete"
    MANAGEMENT = "management"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    role = Column(Enum(UserRole), default=UserRole.ATHLETE)
    
    # Athlete specific fields (nullable for coaches)
    height = Column(Integer, nullable=True) # cm
    weight = Column(Integer, nullable=True) # kg
    personal_best = Column(String, nullable=True) # "10.50"

    sessions = relationship("AnalysisSession", back_populates="owner")
