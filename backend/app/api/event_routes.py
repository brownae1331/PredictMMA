from fastapi import APIRouter, HTTPException
from app.db.database import db_dependency
from app.db.models import models
from app.schemas.event_schemas import Event, MainEvent
from datetime import datetime
import pycountry

router = APIRouter()

def _get_flag_image_url(location: str) -> str:
    """
    Finds a flag image from the location string using flagcdn.com.
    """
    SPECIAL_CASES = {
        "England": "gb-eng",
        "Scotland": "gb-sct",
        "Wales": "gb-wls",
        "Northern Ireland": "gb-nir",
        "Russia": "ru",
    }

    country_name = location.split(",")[-1].strip()
    country = pycountry.countries.get(name=country_name)
    country_code = country.alpha_2 if country else ""

    if country_name in SPECIAL_CASES:
        country_code = SPECIAL_CASES[country_name]

    if not country_code:
        return ""

    return f"https://flagcdn.com/w320/{country_code.lower()}.png"


@router.get("/upcoming")
def get_upcoming_events(db: db_dependency, offset: int = 0, limit: int = 10) -> list[Event]:
    """Return a paginated list of upcoming events from the database."""

    if limit <= 0:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")

    db_events = (
        db.query(models.Event)
        .filter(models.Event.date >= datetime.now())
        .order_by(models.Event.date)
        .offset(offset)
        .limit(limit)
        .all()
    )

    if not db_events:
        raise HTTPException(status_code=404, detail="No upcoming events found")

    return [Event(
        id=event.id,
        title=event.title,
        date=event.date,
        location=event.location,
        location_flag=_get_flag_image_url(event.location),
        organizer=event.organizer,
    ) for event in db_events]

@router.get("/past")
def get_past_events(db: db_dependency, offset: int = 0, limit: int = 10) -> list[Event]:
    """Return a paginated list of past events from the database."""

    if limit <= 0:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")

    db_events = (
        db.query(models.Event)
        .filter(models.Event.date < datetime.now())
        .order_by(models.Event.date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    if not db_events:
        raise HTTPException(status_code=404, detail="No past events found")

    return [Event(
        id=event.id,
        title=event.title,
        date=event.date,
        location=event.location,
        location_flag=_get_flag_image_url(event.location),
        organizer=event.organizer,
    ) for event in db_events]

@router.get("/main-events")
def get_main_events(db: db_dependency, limit: int = 3) -> list[MainEvent]:
    """Return the main events for the home page."""

    db_events = (
        db.query(models.Event)
        .filter(models.Event.date >= datetime.now())
        .order_by(models.Event.date)
        .limit(limit).all()
        )

    if not db_events:
        raise HTTPException(status_code=404, detail="No upcoming events found")
    
    main_events = []
    
    for event in db_events:
        main_event_fight = (
            db.query(models.Fight)
            .filter(models.Fight.event_id == event.id)
            .order_by(models.Fight.match_number.desc())
            .first()
        )

        if not main_event_fight:
            raise HTTPException(status_code=404, detail="No fights found for this event")
        
        main_event_fighter_1 = (
            db.query(models.Fighter)
            .filter(models.Fighter.id == main_event_fight.fighter_1_id)
            .first()
        )

        if not main_event_fighter_1:
            raise HTTPException(status_code=404, detail="Fighter 1 not found")
        
        main_event_fighter_2 = (
            db.query(models.Fighter)
            .filter(models.Fighter.id == main_event_fight.fighter_2_id)
            .first()
        )

        if not main_event_fighter_2:
            raise HTTPException(status_code=404, detail="Fighter 2 not found")

        main_events.append(MainEvent(
            event_id=event.id,
            event_title=event.title,
            event_date=event.date,
            fighter_1_id=main_event_fighter_1.id,
            fighter_2_id=main_event_fighter_2.id,
            fighter_1_name=main_event_fighter_1.name,
            fighter_2_name=main_event_fighter_2.name,
            fighter_1_nickname=main_event_fighter_1.nickname,
            fighter_2_nickname=main_event_fighter_2.nickname,
            fighter_1_image=main_event_fighter_1.image_url,
            fighter_2_image=main_event_fighter_2.image_url,
            fighter_1_ranking=main_event_fighter_1.ranking,
            fighter_2_ranking=main_event_fighter_2.ranking,
        ))

    return main_events