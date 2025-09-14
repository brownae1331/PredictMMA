from fastapi import APIRouter, HTTPException, Query
from app.db.database import db_dependency
from app.db.models import models
from app.schemas.fighter_schemas import Fighter, FighterSearchResponse
router = APIRouter()

@router.get("/")
def get_all_fighters(db: db_dependency) -> list[Fighter]:
    """Get all fighters"""
    fighters = db.query(models.Fighter).all()
    
    return [
        Fighter(
            id=fighter.id,
            name=fighter.name,
            nickname=fighter.nickname,
            image_url=fighter.image_url,
            record=fighter.record,
            ranking=fighter.ranking,
            country=fighter.country,
            city=fighter.city,
            dob=fighter.dob.isoformat() if fighter.dob else None,
            height=fighter.height,
            weight_class=fighter.weight_class,
            association=fighter.association
        )
        for fighter in fighters
    ]

@router.get("/search")
def search_fighters(db: db_dependency, q: str = Query(..., description="Search query")) -> FighterSearchResponse:
    """Search fighters by name, nickname, weight class, or country"""
    query = f"%{q.lower()}%"
    fighters = db.query(models.Fighter).filter(
        models.Fighter.name.ilike(query) |
        models.Fighter.nickname.ilike(query) |
        models.Fighter.weight_class.ilike(query) |
        models.Fighter.country.ilike(query)
    ).all()
    
    fighters = [
            Fighter(
            id=fighter.id,
            name=fighter.name,
            nickname=fighter.nickname,
            image_url=fighter.image_url,
            record=fighter.record,
            ranking=fighter.ranking,
            country=fighter.country,
            city=fighter.city,
            dob=fighter.dob.isoformat() if fighter.dob else None,
            height=fighter.height,
            weight_class=fighter.weight_class,
            association=fighter.association
        )
        for fighter in fighters
    ]
    
    return FighterSearchResponse(
        fighters=fighters,
        total=len(fighters)
    )

@router.get("/{fighter_id}")
def get_fighter_by_id(fighter_id: int, db: db_dependency) -> Fighter:
    """Get a specific fighter by ID"""
    fighter = db.query(models.Fighter).filter(models.Fighter.id == fighter_id).first()
    
    if not fighter:
        raise HTTPException(status_code=404, detail="Fighter not found")
    
    return Fighter(
        id=fighter.id,
        name=fighter.name,
        nickname=fighter.nickname,
        image_url=fighter.image_url,
        record=fighter.record,
        ranking=fighter.ranking,
        country=fighter.country,
        city=fighter.city,
        dob=fighter.dob.isoformat() if fighter.dob else None,
        height=fighter.height,
        weight_class=fighter.weight_class,
        association=fighter.association
    )