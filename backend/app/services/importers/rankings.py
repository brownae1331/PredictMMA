from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.models import Fighter as FighterModel

class RankingsImporter:
    """
    Class for importing rankings.
    """

    def __init__(self, db: Session):
        self.db = db
    
    def apply_rankings(self, rankings: dict[str, list[tuple[str, str]]]) -> None:
        for weight_class, entries in rankings.items():
            for name, rank in entries:
                fighter = (
                    self.db.query(FighterModel)
                    .filter_by(name=name, weight_class=weight_class)
                    .first()
                )
                if fighter:
                    fighter.ranking = rank
                    fighter.last_updated_at = datetime.now()