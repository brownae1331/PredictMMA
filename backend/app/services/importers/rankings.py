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
        missing_fighters = []
        
        print(f"📊 Starting rankings import for {total_fighters} fighters across {len(rankings)} weight classes")
        
        for weight_class, entries in rankings.items():
            print(f"  Processing {weight_class}: {len(entries)} fighters")
            for name, rank in entries:
                fighter = self._find_fighter_by_name_and_weight(name, weight_class)
                
                if not fighter:
                    missing_fighters.append(f"{name} ({weight_class})")
                    missing_count += 1
                    continue

                fighter.ranking = rank
                fighter.last_updated_at = datetime.now()
                ranked_count += 1
                print(f"    ✓ Ranked {name} as {rank} in {weight_class}")
        
        self.db.flush()
        
        if missing_fighters:
            print(f"⚠️  Missing fighters ({len(missing_fighters)}):")
            for mf in missing_fighters[:10]:  # Show first 10 missing fighters
                print(f"    - {mf}")
            if len(missing_fighters) > 10:
                print(f"    ... and {len(missing_fighters) - 10} more")
        
        print(f"✅ Rankings import completed: {ranked_count} fighters ranked, {missing_count} not found")
    
    def _find_fighter_by_name_and_weight(self, name: str, weight_class: str) -> FighterModel:
        """
        Find fighter by name and weight class, trying multiple name formats and weight class variations.
        First try the exact name. Then try the reversed name.
        Also tries weight class variations (e.g., "Lightweight" vs "Light Heavyweight").
        """
        # Try exact match first
        fighter = (
            self.db.query(FighterModel)
            .filter_by(name=name, weight_class=weight_class)
            .first()
        )
        
        if fighter:
            return fighter
            
        # Try reversed name with exact weight class
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
        
        # If still not found, try to find by name only and log weight class mismatch
        fighter = self.db.query(FighterModel).filter_by(name=name).first()
        if fighter:
            print(f"    ⚠️ Found {name} but weight class mismatch: DB has '{fighter.weight_class}', looking for '{weight_class}'")
            # Still return the fighter if found by name only, since fighters can change weight classes
            return fighter
            
        # Try reversed name without weight class constraint
        if len(name_parts) == 2:
            fighter = self.db.query(FighterModel).filter_by(name=reversed_name).first()
            if fighter:
                print(f"    ⚠️ Found {reversed_name} but weight class mismatch: DB has '{fighter.weight_class}', looking for '{weight_class}'")
                return fighter
        
        return None

    def reset_rankings(self) -> None:
        """
        Resets the rankings of all fighters.
        """
        self.db.query(FighterModel).update({"ranking": ""})
        self.db.flush()