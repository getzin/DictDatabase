# backend/crud.py
from sqlalchemy.orm import Session
from backend import models
from backend.security import hash_password
from constants import PROFILE_NAME_MAX_LENGTH, LANGUAGES, CACHE_VALID_FOR
from datetime import datetime, timezone #, timedelta
from sqlalchemy import and_
from backend.models import History

def get_items(db: Session):
    return db.query(models.Item).all()

# --- Users ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, email: str, name: str, password: str):
    user = models.User(
        email=email,
        name=name,
        password=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_user_email_password(db: Session, email: str, password: str) -> bool:
    user = get_user_by_email(db, email)
    if not user:
        return False
    return user.password == password

# ---- helper ----
def _is_valid_lang(code: str) -> bool:
    # LANGUAGES keys are the valid codes (e.g. "en", "de")
    return code in LANGUAGES

# ---- PROFILE CRUD ----
def create_profile(
    db: Session,
    *,
    user_id: int,
    name: str,
    result_lang: str,
    source_lang: str,
    target_lang: str,
):
    # sanitize & validate
    name = (name or "").strip()[:PROFILE_NAME_MAX_LENGTH]
    if not name:
        raise ValueError("Profile name cannot be empty")

    for code in (result_lang, source_lang, target_lang):
        if not _is_valid_lang(code):
            raise ValueError(f"Invalid language code: {code}")

    profile = models.Profile(
        user_id=user_id,
        name=name,
        result_lang=result_lang,
        source_lang=source_lang,
        target_lang=target_lang,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def list_profiles(db: Session, *, user_id: int):
    return (
        db.query(models.Profile)
        .filter(models.Profile.user_id == user_id)
        .order_by(models.Profile.created_at.asc(), models.Profile.id.asc())
        .all()
    )


def get_profile_by_id(db, profile_id: int, user_id: int):
    """
    Retrieve a single profile by ID, ensuring it belongs to the given user.
    """
    from backend.models import Profile
    return (
        db.query(Profile)
        .filter(Profile.id == profile_id, Profile.user_id == user_id)
        .first()
    )

def delete_profile(db: Session, *, profile_id: int, user_id: int) -> bool:
    profile = get_profile_by_id(db, profile_id=profile_id, user_id=user_id)
    if not profile:
        return False
    db.delete(profile)
    db.commit()
    return True

def get_cached_history(db, profile_id, term, source_lang, target_lang):
    """
    Returns cached search if it's still valid (within CACHE_VALID_FOR).
    """
    from backend.models import History
    cutoff = datetime.now(timezone.utc) - CACHE_VALID_FOR
    return (
        db.query(History)
        .filter(
            History.profile_id == profile_id,
            History.term == term,
            History.source_lang == source_lang,
            History.target_lang == target_lang,
            History.created_at >= cutoff,
        )
        .first()
    )

def add_history_entry(db, profile_id, term, source_lang, target_lang, json_response):
    # Check if an identical entry already exists
    existing = (
        db.query(History)
        .filter(
            and_(
                History.profile_id == profile_id,
                History.term == term,
                History.source_lang == source_lang,
                History.target_lang == target_lang,
            )
        )
        .first()
    )

    if existing:
        # Update instead of duplicate
        existing.json_response = json_response
        existing.created_at = datetime.now(timezone.utc)
    else:
        new_entry = History(
            profile_id=profile_id,
            term=term,
            source_lang=source_lang,
            target_lang=target_lang,
            json_response=json_response,
        )
        db.add(new_entry)

    db.commit()

def get_history_for_profile(db, profile_id):
    from backend.models import History
    return (
        db.query(History)
        .filter(History.profile_id == profile_id)
        .order_by(History.created_at.desc())
        .all()
    )

def clear_history_for_profile(db, profile_id):
    from backend.models import History
    db.query(History).filter(History.profile_id == profile_id).delete()
    db.commit()