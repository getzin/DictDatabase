# backend/routes/user_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend import crud, models, database
from backend.schemas import (
    UserCreate, UserLogin, UserOut,
    UpdateApiKeyRequest, ChangePasswordRequest
)
from backend.security import verify_password, hash_password
from constants import (
    API_KEY_MAX_LENGTH,
    PASSWORD_ALLOWED_CHARS_REGEX,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
)

router = APIRouter(prefix="/users", tags=["Users"])


# --- Register ---
@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(database.get_db)):
    if payload.password != payload.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if len(payload.password) < PASSWORD_MIN_LENGTH or len(payload.password) > PASSWORD_MAX_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Password must be between {PASSWORD_MIN_LENGTH} and {PASSWORD_MAX_LENGTH} characters",
        )

    if not PASSWORD_ALLOWED_CHARS_REGEX.match(payload.password):
        raise HTTPException(status_code=400, detail="Password contains invalid characters")

    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = crud.create_user(db, payload.email, payload.name, payload.password)
    return user


# --- Login ---
@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "api_key": user.api_key,
    }


# --- Update API Key ---
@router.post("/update-api-key")
def update_api_key(payload: UpdateApiKeyRequest, db: Session = Depends(database.get_db)):
    api_key = payload.api_key.strip()

    if not api_key:
        raise HTTPException(status_code=400, detail="API key cannot be empty")

    if len(api_key) > API_KEY_MAX_LENGTH:
        raise HTTPException(status_code=400, detail=f"API key too long (max {API_KEY_MAX_LENGTH} chars)")

    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.api_key = api_key
    db.commit()
    return {"status": "ok", "message": "API key updated successfully"}


# --- Change Password ---
@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(payload.old_password, user.password):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")

    if len(payload.new_password) < PASSWORD_MIN_LENGTH or len(payload.new_password) > PASSWORD_MAX_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Password must be between {PASSWORD_MIN_LENGTH} and {PASSWORD_MAX_LENGTH} characters",
        )

    if not PASSWORD_ALLOWED_CHARS_REGEX.match(payload.new_password):
        raise HTTPException(status_code=400, detail="Password contains invalid characters")

    user.password = hash_password(payload.new_password)
    db.commit()
    return {"status": "ok", "message": "Password changed successfully"}
