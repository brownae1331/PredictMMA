from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db.models.models import Fighter

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_all_fighters(db: Session = Depends(get_db)):
    """Get all fighters"""
    fighters = db.query(Fighter).all()
    
    return [
        {
            "id": fighter.id,
            "name": fighter.name,
            "nickname": fighter.nickname,
            "image_url": fighter.image_url,
            "record": fighter.record,
            "ranking": fighter.ranking,
            "country": fighter.country,
            "city": fighter.city,
            "dob": fighter.dob.isoformat() if fighter.dob else None,
            "height": fighter.height,
            "weight_class": fighter.weight_class,
            "association": fighter.association
        }
        for fighter in fighters
    ]

@router.get("/search", response_model=dict)
def search_fighters(
    q: str = Query(..., description="Search query"),
    db: Session = Depends(get_db)
):
    """Search fighters by name, nickname, weight class, or country"""
    query = f"%{q.lower()}%"
    
    fighters = db.query(Fighter).filter(
        Fighter.name.ilike(query) |
        Fighter.nickname.ilike(query) |
        Fighter.weight_class.ilike(query) |
        Fighter.country.ilike(query)
    ).all()
    
    fighter_list = [
        {
            "id": fighter.id,
            "name": fighter.name,
            "nickname": fighter.nickname,
            "image_url": fighter.image_url,
            "record": fighter.record,
            "ranking": fighter.ranking,
            "country": fighter.country,
            "city": fighter.city,
            "dob": fighter.dob.isoformat() if fighter.dob else None,
            "height": fighter.height,
            "weight_class": fighter.weight_class,
            "association": fighter.association
        }
        for fighter in fighters
    ]
    
    return {
        "fighters": fighter_list,
        "total": len(fighter_list)
    }

@router.get("/{fighter_id}", response_model=dict)
def get_fighter_by_id(fighter_id: int, db: Session = Depends(get_db)):
    """Get a specific fighter by ID"""
    fighter = db.query(Fighter).filter(Fighter.id == fighter_id).first()
    
    if not fighter:
        raise HTTPException(status_code=404, detail="Fighter not found")
    
    return {
        "id": fighter.id,
        "name": fighter.name,
        "nickname": fighter.nickname,
        "image_url": fighter.image_url,
        "record": fighter.record,
        "ranking": fighter.ranking,
        "country": fighter.country,
        "city": fighter.city,
        "dob": fighter.dob.isoformat() if fighter.dob else None,
        "height": fighter.height,
        "weight_class": fighter.weight_class,
        "association": fighter.association
    }
