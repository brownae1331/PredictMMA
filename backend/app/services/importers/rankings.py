from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.models import Fighter as FighterModel

class RankingsImporter:
    """
    Class for importing rankings.
    """

    def __init__(self, db: Session):
        self.db = db
        self.reset_rankings()
    
    def apply_rankings(self, rankings: dict[str, list[tuple[str, str]]]) -> None:
        """
        Applies the rankings to the fighters.
        """
        for weight_class, entries in rankings.items():
            for name, rank in entries:
                fighter = (
                    self.db.query(FighterModel)
                    .filter_by(name=name, weight_class=weight_class)
                    .first()
                )
                
                if not fighter:
                    raise ValueError(f"Fighter with name {name} and weight class {weight_class} not found")

                fighter.ranking = rank
                fighter.last_updated_at = datetime.now()

    def reset_rankings(self) -> None:
        """
        Resets the rankings of all fighters.
        """
        self.db.query(FighterModel).update({"ranking": ""})