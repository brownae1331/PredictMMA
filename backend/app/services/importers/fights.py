from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.models import (
    Fight as FightModel,
    Event as EventModel,
    Fighter as FighterModel,
)
from app.schemas.sherdog_schemas import Fight as FightSchema

class FightsImporter:
    """
    Class for importing fights.
    """

    def __init__(self, db: Session):
        self.db = db

    def upsert(self, fight: FightSchema) -> FightModel:
        event = (
            self.db.query(EventModel)
            .filter_by(url=fight.event_url)
            .first()
        )
        if not event:
            raise ValueError(f"Event with URL {fight.event_url} not found")
        
        fighter_1 = (
            self.db.query(FighterModel)
            .filter_by(url=fight.fighter_1_url)
            .first()
        )
        if not fighter_1:
            raise ValueError(f"Fighter with URL {fight.fighter_1_url} not found")
        
        fighter_2 = (
            self.db.query(FighterModel)
            .filter_by(url=fight.fighter_2_url)
            .first()
        )
        if not fighter_2:
            raise ValueError(f"Fighter with URL {fight.fighter_2_url} not found")

        existing = (
            self.db.query(FightModel)
            .filter_by(event_id=event.id, match_number=fight.match_number)
            .first()
        )
        if existing:
            existing.event_id = event.id
            existing.fighter_1_id = fighter_1.id
            existing.fighter_2_id = fighter_2.id
            existing.match_number = fight.match_number
            existing.weight_class = fight.weight_class
            existing.winner = fight.winner
            existing.method = fight.method
            existing.round = fight.round
            existing.time = fight.time
            existing.last_updated_at = datetime.now()
            return existing
        
        new_fight = FightModel(
            event_id=event.id,
            fighter_1_id=fighter_1.id,
            fighter_2_id=fighter_2.id,
            match_number=fight.match_number,
            weight_class=fight.weight_class,
            winner=fight.winner,
            method=fight.method,
            round=fight.round,
            time=fight.time,
            last_updated_at=datetime.now(),
        )
        self.db.add(new_fight)
        self.db.flush()
        return new_fight