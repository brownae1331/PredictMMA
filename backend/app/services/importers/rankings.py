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
        total_fighters = sum(len(entries) for entries in rankings.values())
        ranked_count = 0
        missing_count = 0
        
        print(f"📊 Starting rankings import for {total_fighters} fighters across {len(rankings)} weight classes")
        
        for weight_class, entries in rankings.items():
            for name, rank in entries:
                fighter = self._find_fighter_by_name_and_weight(name, weight_class)
                
                if not fighter:
                    print(f"⚠️  Fighter not found: {name} ({weight_class})")
                    missing_count += 1
                    continue

                fighter.ranking = rank
                fighter.last_updated_at = datetime.now()
                ranked_count += 1
        
        print(f"✅ Rankings import completed: {ranked_count} fighters ranked, {missing_count} not found")
    
    def _find_fighter_by_name_and_weight(self, name: str, weight_class: str) -> FighterModel:
        """
        Find fighter by name and weight class, trying multiple name formats.
        First try the exact name. Then try the reversed name.
        """
        fighter = (
            self.db.query(FighterModel)
            .filter_by(name=name, weight_class=weight_class)
            .first()
        )
        
        if fighter:
            return fighter
            
        name_parts = name.split()
        if len(name_parts) == 2:
            reversed_name = f"{name_parts[1]} {name_parts[0]}"
            fighter = (
                self.db.query(FighterModel)
                .filter_by(name=reversed_name, weight_class=weight_class)
                .first()
            )
            
            if fighter:
                return fighter
        
        return None

    def reset_rankings(self) -> None:
        """
        Resets the rankings of all fighters.
        """
        self.db.query(FighterModel).update({"ranking": ""})