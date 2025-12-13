from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.models import Fighter as FighterModel
from app.schemas.sherdog_schemas import Fighter as FighterSchema
from app.schemas.scraper_schemas import Fighter as ScraperFighterSchema

class FightersImporter:
    """
    Class for importing fighters.
    Supports both sherdog_schemas and scraper_schemas.
    """

    def __init__(self, db: Session):
        self.db = db

    def upsert(self, fighter: FighterSchema | ScraperFighterSchema) -> FighterModel:
        # Handle scraper_schemas.Fighter (from ufcstats)
        if isinstance(fighter, ScraperFighterSchema):
            return self._upsert_from_scraper(fighter)
        
        # Handle sherdog_schemas.Fighter (existing)
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
    
    def _upsert_from_scraper(self, fighter: ScraperFighterSchema) -> FighterModel:
        """Import fighter from ufcstats scraper schema."""
        # Build record string from wins/losses/draws
        record = f"{fighter.wins}-{fighter.losses}-{fighter.draws}" if (fighter.wins or fighter.losses or fighter.draws) else None
        
        existing = (
            self.db.query(FighterModel)
            .filter_by(url=fighter.url)
            .first()
        )
        
        if not existing:
            # Try to find by name (without weight_class since scraper doesn't provide it)
            existing = (
                self.db.query(FighterModel)
                .filter_by(name=fighter.name)
                .first()
            )
            
        if existing:
            existing.url = fighter.url
            existing.name = fighter.name
            existing.nickname = fighter.nickname
            existing.record = record
            existing.height = fighter.height
            # Don't overwrite fields not available from scraper
            # existing.image_url, ranking, country, city, dob, weight_class, association remain unchanged
            existing.last_updated_at = datetime.now()
            return existing
          
        new_fighter = FighterModel(
            url=fighter.url,
            name=fighter.name,
            nickname=fighter.nickname,
            image_url=None,
            record=record,
            ranking=None,
            country=None,
            city=None,
            dob=None,
            height=fighter.height,
            weight_class=None,
            association=None,
            last_updated_at=datetime.now(),
        )
        self.db.add(new_fighter)
        self.db.flush()
        return new_fighter