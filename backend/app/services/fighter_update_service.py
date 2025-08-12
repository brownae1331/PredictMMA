from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models.models import Fighter as FighterModel
from app.services.scrapers.sherdog_scraper import SherdogScraper
from app.services.scrapers.ufc_ranking_scraper import UFCRankingScraper


def update_all_fighters(db: Session, *, update_rankings: bool = True) -> None:
    """Refreshes the stats of every fighter currently stored in the database.

    Parameters
    ----------
    db : Session
        An active SQLAlchemy session.
    update_rankings : bool, optional
        If ``True`` (default) the fighter rankings will be refreshed after the
        individual fighter updates complete.
    """

    scraper = SherdogScraper()

    fighters: List[FighterModel] = db.query(FighterModel).all()
    total = len(fighters)
    print(f"\n=========== FIGHTER DATA REFRESH ===========")
    print(f"Found {total} fighters in database — starting update …")

    updated_count = 0
    skipped_count = 0

    for idx, fighter_row in enumerate(fighters, start=1):
        if fighter_row.url == "unknown":
            skipped_count += 1
            print(f"[{idx}/{total}] Skipping placeholder fighter (id={fighter_row.id})")
            continue

        print(f"[{idx}/{total}] Updating: {fighter_row.name} ({fighter_row.url}) …")
        try:
            fighter_data = scraper.get_fighter_stats(fighter_row.url)
        except Exception as exc:
            print(f"      ⚠️  Failed to scrape {fighter_row.url}: {exc}")
            skipped_count += 1
            continue

        fighter_row.name = fighter_data.name
        fighter_row.nickname = fighter_data.nickname
        fighter_row.image_url = fighter_data.image_url
        fighter_row.record = fighter_data.record
        fighter_row.country = fighter_data.country
        fighter_row.city = fighter_data.city
        fighter_row.dob = fighter_data.dob
        fighter_row.height = fighter_data.height
        fighter_row.weight_class = fighter_data.weight_class
        fighter_row.association = fighter_data.association

        updated_count += 1

        if updated_count % 50 == 0:
            db.flush()

    db.commit()
    print(f"✓ Finished updating fighters — {updated_count} updated, {skipped_count} skipped.")

    # ── RANKINGS ───────────────────────────────────────────────────────────
    if update_rankings:
        _refresh_rankings(db)


def _refresh_rankings(db: Session) -> None:
    """Fetch current UFC rankings and apply them to matching fighters."""
    print("\nUpdating fighter rankings …")
    ranking_scraper = UFCRankingScraper()
    rankings_dict = ranking_scraper.get_ufc_rankings()

    updated = 0
    for weight_class, ranked_fighters in rankings_dict.items():
        for name, rank in ranked_fighters:
            fighter_row = (
                db.query(FighterModel)
                .filter(func.lower(FighterModel.name) == name.lower())
                .filter(FighterModel.weight_class.ilike(f"%{weight_class}%"))
                .first()
            )
            if fighter_row:
                fighter_row.ranking = rank
                updated += 1

    db.commit()
    print(f"✓ Applied rankings to {updated} fighters.") 