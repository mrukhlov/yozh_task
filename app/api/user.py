"""User API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[User])
def list_users(
    current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    users = db.query(UserModel).all()
    return users


@router.put("/me", response_model=User)
def update_me(
    update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if update.email:
        current_user.email = update.email
    if update.username:
        current_user.username = update.username
    if update.password:
        from app.core.security import get_password_hash

        current_user.hashed_password = get_password_hash(update.password)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=204)
def delete_me(
    db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    db.delete(current_user)
    db.commit()
    return None
