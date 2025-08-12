from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.models import Fighter as FighterModel
from app.schemas.sherdog_schemas import Fighter as FighterSchema

class FightersImporter:
    """
    Class for importing fighters.
    """

    def __init__(self, db: Session):
        self.db = db

    def upsert(self, fighter: FighterSchema) -> FighterModel:
        existing = (
            self.db.query(FighterModel)
            .filter_by(url=fighter.url)
            .first()
        )
        
        if not existing:
            existing = (
                self.db.query(FighterModel)
                .filter_by(name=fighter.name, weight_class=fighter.weight_class)
                .first()
            )
            
        if existing:
            existing.url = fighter.url
            existing.name = fighter.name
            existing.nickname = fighter.nickname
            existing.image_url = fighter.image_url
            existing.record = fighter.record
            existing.ranking = fighter.ranking
            existing.country = fighter.country
            existing.city = fighter.city
            existing.dob = fighter.dob
            existing.height = fighter.height
            existing.weight_class = fighter.weight_class
            existing.association = fighter.association
            existing.last_updated_at = datetime.now()
            return existing
          
        new_fighter = FighterModel(
            url=fighter.url,
            name=fighter.name,
            nickname=fighter.nickname,
            image_url=fighter.image_url,
            record=fighter.record,
            ranking=fighter.ranking,
            country=fighter.country,
            city=fighter.city,
            dob=fighter.dob,
            height=fighter.height,
            weight_class=fighter.weight_class,
            association=fighter.association,
            last_updated_at=datetime.now(),
        )
        self.db.add(new_fighter)
        self.db.flush()
        return new_fighter