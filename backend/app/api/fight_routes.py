from fastapi import APIRouter, HTTPException
from app.db.database import db_dependency
from app.db.models import models
from app.schemas.fight_schemas import Fight
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

@router.get("/{event_id}")
def get_fights_by_event(event_id: int, db: db_dependency) -> list[Fight]:
    """Return a list of fights for a given event."""

    db_fights = (
        db.query(models.Fight)
        .filter(models.Fight.event_id == event_id)
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
            fighter_1_id=fight_fighter_1.id,
            fighter_2_id=fight_fighter_2.id,
            fighter_1_name=fight_fighter_1.name,
            fighter_2_name=fight_fighter_2.name,
            fighter_1_image=fight_fighter_1.image_url,
            fighter_2_image=fight_fighter_2.image_url,
            fighter_1_ranking=fight_fighter_1.ranking,
            fighter_2_ranking=fight_fighter_2.ranking,
            fighter_1_flag=_get_flag_image_url(fight_fighter_1.country),
            fighter_2_flag=_get_flag_image_url(fight_fighter_2.country),
            match_number=fight.match_number,
            weight_class=fight.weight_class,
            winner=fight.winner,
            method=fight.method,
            round=fight.round,
            time=fight.time
        ))

    return fights