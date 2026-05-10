# backend/routes/search_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests, json
from backend import crud, database
from backend.models import History

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/")
def perform_search(profile_id: int, user_id: int, term: str, db: Session = Depends(database.get_db)):
    """
    Executes a dictionary search via PONS API or returns cached version.
    """
    if not term.strip():
        raise HTTPException(status_code=400, detail="Empty search term")

    profile = crud.get_profile_by_id(db, profile_id=profile_id, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found or does not belong to this user")

    # 1️⃣ Try cache
    cached = crud.get_cached_history(db, profile.id, term, profile.source_lang, profile.target_lang)
    if cached:
        return {"cached": True, "data": json.loads(cached.json_response)}

    # 2️⃣ Fetch from PONS
    user = profile.user
    if not user.api_key:
        raise HTTPException(status_code=400, detail="User has no API key")

    headers = {"X-Secret": user.api_key}
    dict_code = "".join(sorted([profile.source_lang, profile.target_lang]))
    url = f"https://api.pons.com/v1/dictionary?q={term}&l={dict_code}"

    print(url)
    print(headers)

    response = requests.get(url, headers=headers)

    print(response)

    # --- Error handling for PONS responses ---
    if response.status_code == 403:
        raise HTTPException(status_code=403, detail="Invalid or missing API key for PONS API")
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail="No dictionary found for selected languages")
    elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"PONS API error ({response.status_code})")

    json_data = response.json()

    if json_data:
        crud.add_history_entry(db, profile.id, term, profile.source_lang, profile.target_lang, json.dumps(json_data))

    return {"cached": False, "data": json_data}

@router.get("/history/{profile_id}")
def get_history(profile_id: int, db: Session = Depends(database.get_db)):
    """
    Returns all history entries for a profile.
    """
    return crud.get_history_for_profile(db, profile_id)

@router.delete("/history/{profile_id}")
def clear_history(profile_id: int, db: Session = Depends(database.get_db)):
    db.query(History).filter(History.profile_id == profile_id).delete(synchronize_session=False)
    db.commit()
    return {"detail": "History cleared"}

@router.delete("/history/{profile_id}/{term}")
def delete_history_item(profile_id: int, term: str, db: Session = Depends(database.get_db)):
    deleted = (
        db.query(History)
        .filter(History.profile_id == profile_id, History.term == term)
        .delete(synchronize_session=False)
    )
    db.commit()

    if deleted == 0:
        return {"detail": f"No history entries found for term '{term}'"}, 404
    return {"detail": f"Deleted {deleted} entries for term '{term}'"}