from fastapi import APIRouter, HTTPException
from app.db.database import db_dependency
from app.db.models import models
from app.schemas.fight_schemas import Fight, FightResult, ResultType
from datetime import datetime
from zoneinfo import ZoneInfo
from app.core.utils.string_utils import simplify_method, get_flag_image_url

router = APIRouter()


@router.get("/event/{event_id}")
def get_fights_by_event(event_id: int, db: db_dependency) -> list[Fight]:
    """Return a list of fights for a given event."""

    db_fights = (
        db.query(models.Fight)
        .filter(models.Fight.event_id == event_id)
        .order_by(models.Fight.match_number)
        .all()
    )

    if not db_fights:
        raise HTTPException(status_code=404, detail="No fights found for this event")
    
    fights = []

    for fight in db_fights:
        fight_fighter_1 = (
            db.query(models.Fighter)
            .filter(models.Fighter.id == fight.fighter_1_id)
            .first()
        )

        if not fight_fighter_1:
            raise HTTPException(status_code=404, detail="Fighter 1 not found")
        
        fight_fighter_2 = (
            db.query(models.Fighter)
            .filter(models.Fighter.id == fight.fighter_2_id)
            .first()
        )
        
        if not fight_fighter_2:
            raise HTTPException(status_code=404, detail="Fighter 2 not found")
        
        fights.append(Fight(
            id=fight.id,
            fighter_1_id=fight_fighter_1.id,
            fighter_2_id=fight_fighter_2.id,
            fighter_1_name=fight_fighter_1.name,
            fighter_2_name=fight_fighter_2.name,
            fighter_1_image=fight_fighter_1.image_url,
            fighter_2_image=fight_fighter_2.image_url,
            fighter_1_ranking=fight_fighter_1.ranking,
            fighter_2_ranking=fight_fighter_2.ranking,
            fighter_1_flag=get_flag_image_url(fight_fighter_1.country),
            fighter_2_flag=get_flag_image_url(fight_fighter_2.country),
            weight_class=fight.weight_class,
            winner=fight.winner,
            method=simplify_method(fight.method),
            round=fight.round,
            time=fight.time
        ))

    return fights

@router.get("/fight/{fight_id}")
def get_fight_by_id(fight_id: int, db: db_dependency) -> Fight:
    """Return a fight by its ID."""

    db_fight = (
        db.query(models.Fight)
        .filter(models.Fight.id == fight_id)
        .first()
    )

    if not db_fight:
        raise HTTPException(status_code=404, detail="Fight not found")
    
    fight_fighter_1 = (
        db.query(models.Fighter)
        .filter(models.Fighter.id == db_fight.fighter_1_id)
        .first()
    )

    if not fight_fighter_1:
        raise HTTPException(status_code=404, detail="Fighter 1 not found")
    
    fight_fighter_2 = (
        db.query(models.Fighter)
        .filter(models.Fighter.id == db_fight.fighter_2_id)
        .first()
    )

    if not fight_fighter_2:
        raise HTTPException(status_code=404, detail="Fighter 2 not found")
    
    return Fight(
        id=db_fight.id,
        fighter_1_id=fight_fighter_1.id,
        fighter_2_id=fight_fighter_2.id,
        fighter_1_name=fight_fighter_1.name,
        fighter_2_name=fight_fighter_2.name,
        fighter_1_image=fight_fighter_1.image_url,
        fighter_2_image=fight_fighter_2.image_url,
        fighter_1_ranking=fight_fighter_1.ranking,
        fighter_2_ranking=fight_fighter_2.ranking,
        fighter_1_flag=get_flag_image_url(fight_fighter_1.country),
        fighter_2_flag=get_flag_image_url(fight_fighter_2.country),
        weight_class=db_fight.weight_class,
        winner=db_fight.winner,
        method=simplify_method(db_fight.method),
        round=db_fight.round,
        time=db_fight.time
    )

@router.get("/result/{fight_id}")
def get_fight_result_by_id(fight_id: int, db: db_dependency) -> FightResult | None:
    """Return the result of a fight by its ID."""

    db_fight = (
        db.query(models.Fight)
        .filter(models.Fight.id == fight_id)
        .join(models.Event, models.Fight.event_id == models.Event.id)
        .filter(models.Event.date < datetime.now(ZoneInfo("Europe/London")))
        .first()
    )

    if not db_fight:
        return None
    
    if db_fight.winner == "draw":
        result_type = ResultType.DRAW
        winner_id = None
    elif db_fight.winner == "no contest":
        result_type = ResultType.NO_CONTEST
        winner_id = None
    else:
        result_type = ResultType.WIN
        winner_id = db_fight.fighter_1_id

    if not db_fight.winner:
        raise HTTPException(status_code=404, detail="Fight result not found")
    
    return FightResult(
        result_type=result_type,
        winner_id=winner_id,
        method=simplify_method(db_fight.method),
        round=db_fight.round,
        time=db_fight.time
    )