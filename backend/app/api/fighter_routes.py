from fastapi import APIRouter, HTTPException, Query
from app.db.database import db_dependency
from app.db.models import models
from app.schemas.fighter_schemas import Fighter, FighterSearchResponse
from app.schemas.fight_schemas import FighterFightHistory
from app.core.utils.string_utils import get_flag_image_url
router = APIRouter()

@router.get("/")
def get_all_fighters(
    db: db_dependency, 
    offset: int = Query(0, ge=0, description="Number of fighters to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of fighters to return")
) -> list[Fighter]:
    """Get all fighters with pagination"""
    fighters = db.query(models.Fighter).offset(offset).limit(limit).all()
    
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

@router.get("/{fighter_id}/fights")
def get_fighter_fight_history(fighter_id: int, db: db_dependency) -> list[FighterFightHistory]:
    """Get all fights for a specific fighter"""
    fighter = db.query(models.Fighter).filter(models.Fighter.id == fighter_id).first()
    if not fighter:
        raise HTTPException(status_code=404, detail="Fighter not found")
    
    db_fights = (
        db.query(models.Fight, models.Event)
        .join(models.Event, models.Fight.event_id == models.Event.id)
        .filter(
            (models.Fight.fighter_1_id == fighter_id) | 
            (models.Fight.fighter_2_id == fighter_id)
        )
        .order_by(models.Event.date.desc())
        .all()
    )
    
    fight_history = []
    
    for fight, event in db_fights:
        opponent_id = fight.fighter_2_id if fight.fighter_1_id == fighter_id else fight.fighter_1_id
        opponent = db.query(models.Fighter).filter(models.Fighter.id == opponent_id).first()
        
        if not opponent:
            continue
            
        result = "N/A"
        if fight.winner:
            if fight.winner.lower() == "draw":
                result = "Draw"
            elif fight.winner.lower() == "no contest":
                result = "No Contest"
            elif fight.winner == "fighter_1":
                if fight.fighter_1_id == fighter_id:
                    result = "Win"
                else:
                    result = "Loss"
            else:
                result = "N/A"
        
        fight_history.append(FighterFightHistory(
            id=fight.id,
            event_title=event.title,
            event_date=event.date.isoformat() if event.date else None,
            event_location=event.location,
            opponent_id=opponent.id,
            opponent_name=opponent.name,
            opponent_image=opponent.image_url,
            opponent_country=opponent.country,
            opponent_flag=get_flag_image_url(opponent.country),
            weight_class=fight.weight_class,
            result=result,
            method=fight.method,
            round=fight.round,
            time=fight.time
        ))
    
    return fight_history