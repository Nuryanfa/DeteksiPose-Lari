from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_user
from app.models.user import User as UserModel
from app.schemas import user as user_schema

router = APIRouter()

@router.get("/me", response_model=user_schema.User)
def read_user_me(
    current_user: UserModel = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.post("/", response_model=user_schema.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: user_schema.UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud_user.create(db, obj_in=user_in)
    return user

@router.put("/me", response_model=user_schema.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: user_schema.UserUpdate,
    current_user: UserModel = Depends(deps.get_current_user),
) -> Any:
    """
    Update own user.
    """
    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get("/athletes", response_model=List[user_schema.User])
def read_athletes(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve all athletes (only for Coaches/Management/Admin).
    """
    from app.models.user import UserRole
    
    # Strict Role Check
    allowed_roles = [UserRole.ADMIN, UserRole.MANAGEMENT, UserRole.COACH]
    if current_user.role not in allowed_roles:
         raise HTTPException(
            status_code=403,
            detail="Not authorized to view athlete list",
        )
    
    users = db.query(UserModel).filter(UserModel.role == UserRole.ATHLETE).offset(skip).limit(limit).all()
    return users
