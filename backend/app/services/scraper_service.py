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

    # Early exit if no events were fetched (should not occur due to validation, but safe-guard)
    if not all_events:
        print("No events to persist — exiting scrape.")
        return

    # Map full URL → persisted EventModel (used later for FK look-ups)
    persisted_events: dict[str, EventModel] = {}

    print("\nPersisting events to DB …")
    for event in all_events:
        print(f"  • Event: {event.title} ({event.date.strftime('%Y-%m-%d')})")
        existing = db.query(EventModel).filter_by(url=event.url).first()
        if existing:
            # Optional: update mutable fields in case of changes
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
            db.flush()  # get PK without committing yet
            persisted_events[event.url] = new_event

    db.commit()

    # 2) FIGHTS & FIGHTERS ─────────────────────────────────────────────────

    def get_or_create_fighter(fighter_url: str) -> FighterModel:
        """Return a FighterModel row for the given URL, creating it if necessary."""
        # Check if this fighter already exists in the DB
        fighter_row = db.query(FighterModel).filter_by(url=fighter_url).first()
        if fighter_row:
            return fighter_row

        # Special-case: placeholder for unknown fighters (Sherdog uses `javascript:` links)
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

        # Otherwise scrape real fighter stats
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

    # Previous completed events first
    for event in previous_events:
        print(f"\n▶ Previous Event: {event.title}")
        fights: List[FightSchema] = scraper.get_previous_event_fights(event.url)
        print(f"  → {len(fights)} fights found")
        _upsert_fights(db, fights, persisted_events[event.url], get_or_create_fighter)

    # Upcoming events
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
    """Persist fights for a single event, creating fighter rows as needed."""
    for fight in fights:
        exists = (
            db.query(FightModel)
            .filter_by(event_id=event_row.id, match_number=fight.match_number)
            .first()
        )
        if exists:
            continue

        fighter_1_row = get_or_create_fighter(fight.fighter_1_url)
        fighter_2_row = get_or_create_fighter(fight.fighter_2_url)

        db_fight = FightModel(
            event_id=event_row.id,
            fighter_1_id=fighter_1_row.id,
            fighter_2_id=fighter_2_row.id,
            match_number=fight.match_number,
            weight_class=fight.weight_class,
            winner=fight.winner,
            method=fight.method,
            round=fight.round,
            time=fight.time,
        )
        db.add(db_fight)
        print(f"      ✓ Added fight #{fight.match_number}: {fighter_1_row.name} vs {fighter_2_row.name}")
    # Flush but not commit inside the loop to avoid excessive commits
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
            # Match on fighter name (case-insensitive) and weight class (substring match to cope with "Women's" prefix)
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