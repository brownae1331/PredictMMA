from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.services.sherdog_scraper import SherdogScraper
from app.services.ufc_ranking_scraper import UFCRankingScraper
from app.db.models.models import Event as EventModel, Fight as FightModel, Fighter as FighterModel
from app.schemas.sherdog_schemas import Event as EventSchema, Fight as FightSchema, Fighter as FighterSchema


def scrape_ufc_data(db: Session, *, scrape_previous: bool = True, scrape_upcoming: bool = True) -> None:
    """High-level orchestrator that pulls UFC data from Sherdog and seeds the database.

    Parameters
    ----------
    scrape_previous : bool, optional
        If True (default) the scraper will fetch and persist data for past UFC events.
    scrape_upcoming : bool, optional
        If True (default) the scraper will fetch and persist data for upcoming UFC events.

    Workflow:
        1. Depending on the flags provided, scrape previous and/or upcoming UFC events and upsert them.
        2. For every event, scrape its fights and upsert them (including their fighters).
        3. For every unique fighter found, scrape detailed stats and upsert them.
    """
    # Validate input flags
    if not scrape_previous and not scrape_upcoming:
        raise ValueError("At least one of 'scrape_previous' or 'scrape_upcoming' must be True.")

    print("\n================ UFC DATA SCRAPER ================")
    scraper = SherdogScraper()

    # 1) EVENTS ────────────────────────────────────────────────────────────
    previous_events: List[EventSchema] = []
    upcoming_events: List[EventSchema] = []

    if scrape_previous:
        print("Fetching previous UFC events …")
        previous_events = scraper.get_previous_ufc_events()
        print(f"  → {len(previous_events)} previous events scraped")

    if scrape_upcoming:
        print("Fetching upcoming UFC events …")
        upcoming_events = scraper.get_upcoming_ufc_events()
        print(f"  → {len(upcoming_events)} upcoming events scraped")

    all_events = previous_events + upcoming_events

    if not all_events:
        print("No events to persist — exiting scrape.")
        return

    persisted_events: dict[str, EventModel] = {}

    print("\nPersisting events to DB …")
    for event in all_events:
        print(f"  • Event: {event.title} ({event.date.strftime('%Y-%m-%d')})")
        existing = db.query(EventModel).filter_by(url=event.url).first()
        if existing:
            existing.title = event.title
            existing.date = event.date
            existing.location = event.location
            existing.organizer = event.organizer
            persisted_events[event.url] = existing
        else:
            existing = db.query(EventModel).filter_by(date=event.date, location=event.location, organizer=event.organizer).first()
            if existing:
                existing.url = event.url
                existing.title = event.title
                existing.date = event.date
                existing.location = event.location
                existing.organizer = event.organizer
                persisted_events[event.url] = existing
            else:
                new_event = EventModel(
                    url=event.url,
                    title=event.title,
                    date=event.date,
                    location=event.location,
                    organizer=event.organizer,
                )
                db.add(new_event)
                db.flush()
                persisted_events[event.url] = new_event

    db.commit()

    # 2) FIGHTS & FIGHTERS ─────────────────────────────────────────────────

    def get_or_create_fighter(fighter_url: str) -> FighterModel:
        """
        Return a FighterModel row for the given URL, creating it if necessary.
        If the fighter already exists, update their stats if they are not a placeholder.
        """
        fighter_row = db.query(FighterModel).filter_by(url=fighter_url).first()
        if fighter_row:
            if fighter_url != "unknown":
                print(f"    ↪ Updating fighter stats: {fighter_url}")
                fighter_data: FighterSchema = scraper.get_fighter_stats(fighter_url)
                fighter_row.name = fighter_data.name
                fighter_row.nickname = fighter_data.nickname
                fighter_row.image_url = fighter_data.image_url
                fighter_row.record = fighter_data.record
                fighter_row.country = fighter_data.country
                fighter_row.city = fighter_data.city
                fighter_row.age = fighter_data.age
                fighter_row.dob = fighter_data.dob
                fighter_row.height = fighter_data.height
                fighter_row.weight_class = fighter_data.weight_class
                fighter_row.association = fighter_data.association
                db.flush()
                print(f"      ✓ Updated fighter: {fighter_data.name}")
            return fighter_row

        if fighter_url == "unknown":
            fighter_row = FighterModel(
                url="unknown",
                name="Unknown Fighter",
                nickname="",
                image_url="",
                record="0-0-0, 0 NC",
                country="",
                city="",
                age=None,
                dob=None,
                height="",
                weight_class="",
                association="",
            )
            db.add(fighter_row)
            db.flush()
            print("      ✓ Added placeholder 'Unknown Fighter'")
            return fighter_row

        print(f"    ↪ Scraping fighter stats: {fighter_url}")
        fighter_data: FighterSchema = scraper.get_fighter_stats(fighter_url)
        fighter_row = FighterModel(
            url=fighter_data.url,
            name=fighter_data.name,
            nickname=fighter_data.nickname,
            image_url=fighter_data.image_url,
            record=fighter_data.record,
            country=fighter_data.country,
            city=fighter_data.city,
            age=fighter_data.age,
            dob=fighter_data.dob,
            height=fighter_data.height,
            weight_class=fighter_data.weight_class,
            association=fighter_data.association,
        )
        db.add(fighter_row)
        print(f"      ✓ Added fighter: {fighter_data.name}")
        db.flush()
        return fighter_row

    print("\nScraping fights for each event …")

    for event in previous_events:
        print(f"\n▶ Previous Event: {event.title}")
        fights: List[FightSchema] = scraper.get_previous_event_fights(event.url)
        print(f"  → {len(fights)} fights found")
        _upsert_fights(db, fights, persisted_events[event.url], get_or_create_fighter)

    for event in upcoming_events:
        print(f"\n▶ Upcoming Event: {event.title}")
        fights: List[FightSchema] = scraper.get_upcoming_event_fights(event.url)
        print(f"  → {len(fights)} fights found")
        _upsert_fights(db, fights, persisted_events[event.url], get_or_create_fighter)

    db.commit()

    # 3) RANKINGS ──────────────────────────────────────────────────────────
    _update_fighter_rankings(db)


def _upsert_fights(
    db: Session,
    fights: List[FightSchema],
    event_row: EventModel,
    get_or_create_fighter,
) -> None:
    """Persist fights for a single event, handling inserts, updates, and cancellations."""

    scraped_by_number: dict[int, FightSchema] = {f.match_number: f for f in fights}

    existing_fights: list[FightModel] = (
        db.query(FightModel).filter_by(event_id=event_row.id).all()
    )
    existing_by_number: dict[int, FightModel] = {
        f.match_number: f for f in existing_fights
    }

    # ── INSERT OR UPDATE ────────────────────────────────────────────────
    for match_number, scraped in scraped_by_number.items():
        fighter_1_row = get_or_create_fighter(scraped.fighter_1_url)
        fighter_2_row = get_or_create_fighter(scraped.fighter_2_url)

        if match_number in existing_by_number:
            db_fight = existing_by_number[match_number]
            changes_made = False

            if db_fight.fighter_1_id != fighter_1_row.id:
                db_fight.fighter_1_id = fighter_1_row.id
                changes_made = True
            if db_fight.fighter_2_id != fighter_2_row.id:
                db_fight.fighter_2_id = fighter_2_row.id
                changes_made = True

            for attr in [
                "weight_class",
                "winner",
                "method",
                "round",
                "time",
            ]:
                new_val = getattr(scraped, attr)
                if getattr(db_fight, attr) != new_val:
                    setattr(db_fight, attr, new_val)
                    changes_made = True

            if changes_made:
                print(
                    f"      ↻ Updated fight #{match_number}: {fighter_1_row.name} vs {fighter_2_row.name}"
                )
        else:
            db_fight = FightModel(
                event_id=event_row.id,
                fighter_1_id=fighter_1_row.id,
                fighter_2_id=fighter_2_row.id,
                match_number=scraped.match_number,
                weight_class=scraped.weight_class,
                winner=scraped.winner,
                method=scraped.method,
                round=scraped.round,
                time=scraped.time,
            )
            db.add(db_fight)
            print(
                f"      ✓ Added fight #{scraped.match_number}: {fighter_1_row.name} vs {fighter_2_row.name}"
            )

    # ── CANCELLATIONS ──────────────────────────────────────────────────
    for match_number, db_fight in existing_by_number.items():
        if match_number not in scraped_by_number:
            print(
                f"      ✗ Removed cancelled fight #{match_number}: {db_fight.fighter_1.name} vs {db_fight.fighter_2.name}"
            )
            db.delete(db_fight)

    db.flush()


def _update_fighter_rankings(db: Session) -> None:
    """Fetch current UFC rankings and update Fighter rows accordingly."""
    print("\nFetching current UFC rankings …")
    ranking_scraper = UFCRankingScraper()
    rankings_dict = ranking_scraper.get_ufc_rankings()

    print("Persisting fighter rankings to DB …")
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
    print(f"  ✓ Updated rankings for {updated} fighters.") 