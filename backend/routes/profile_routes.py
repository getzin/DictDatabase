# backend/routes/profile_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend import crud, database
from backend.schemas import ProfileCreate, ProfileOut

router = APIRouter(prefix="/profiles", tags=["Profiles"])


# --- Create Profile ---
@router.post("", response_model=ProfileOut)
def create_profile(profile: ProfileCreate, db: Session = Depends(database.get_db)):
    """
    Create a new profile for a given user.
    """
    try:
        new_profile = crud.create_profile(
            db=db,
            user_id=profile.user_id,
            name=profile.name,
            result_lang=profile.result_lang,
            source_lang=profile.source_lang,
            target_lang=profile.target_lang,
        )
        return new_profile
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- List Profiles ---
@router.get("", response_model=list[ProfileOut])
def list_profiles(user_id: int, db: Session = Depends(database.get_db)):
    """
    Get all profiles belonging to a user.
    """
    profiles = crud.list_profiles(db=db, user_id=user_id)
    return profiles


# --- Delete Profile ---
@router.delete("/{profile_id}")
def delete_profile(profile_id: int, user_id: int, db: Session = Depends(database.get_db)):
    """
    Delete a profile.
    """
    deleted = crud.delete_profile(db=db, profile_id=profile_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"detail": "Profile deleted successfully"}
