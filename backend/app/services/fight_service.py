from typing import List
from sqlalchemy.orm import Session

from app.schemas.sherdog_schemas import Fight as FightSchema
from app.db.models.models import Fight as FightModel


def upsert_fights(fights: List[FightSchema], db: Session) -> None:
    """Insert fights (and any referenced fighters) into the database if they don't already exist.

    Args:
        fights: List of FightSchema objects scraped from Sherdog.
        db: SQLAlchemy session.
    """
    for fight in fights:
        # Avoid duplicate fight entries via composite primary key
        exists = (
            db.query(FightModel)
            .filter_by(event_url=fight.event_url, fight_idx=fight.fight_idx)
            .first()
        )
        if exists:
            continue

        db_fight = FightModel(
            event_url=fight.event_url,
            fight_idx=fight.fight_idx,
            fighter_1_link=fight.fighter_1_link,
            fighter_2_link=fight.fighter_2_link,
            fight_weight=fight.fight_weight,
            fight_winner=fight.fight_winner,
            fight_method=fight.fight_method,
            fight_round=fight.fight_round,
            fight_time=fight.fight_time,
        )
        db.add(db_fight)

    db.commit() 