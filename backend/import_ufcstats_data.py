#!/usr/bin/env python3
"""
Script to import events, fights, and fighters from ufcstats.com into the database.

Usage:
    python import_ufcstats_data.py [--events-only] [--fighters-only] [--fights-only] [--limit N]

Examples:
    # Import everything
    python import_ufcstats_data.py

    # Import only events
    python import_ufcstats_data.py --events-only

    # Import only fighters
    python import_ufcstats_data.py --fighters-only

    # Import fights for a specific event (requires event URL)
    python import_ufcstats_data.py --fights-only --event-url <URL>

    # Import only first 10 events
    python import_ufcstats_data.py --limit 10
"""

import argparse
import sys
from contextlib import contextmanager
from typing import Optional

from app.db.database import sessionLocal
from app.services.importers.events import EventsImporter
from app.services.importers.fighters import FightersImporter
from app.services.importers.fights import FightsImporter
from app.services.scrapers.ufcstats.event_scraper import UFCStatsEventScraper
from app.services.scrapers.ufcstats.fight_scraper import UFCStatsFightScraper
from app.services.scrapers.ufcstats.fighter_scraper import UFCStatsFighterScraper


@contextmanager
def session_scope():
    """Database session context manager."""
    db = sessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def import_events(limit: Optional[int] = None):
    """Import all events from ufcstats."""
    print("=" * 60)
    print("Importing Events from UFCStats")
    print("=" * 60)
    
    scraper = UFCStatsEventScraper()
    events = scraper.get_all_events()
    
    if limit:
        events = events[:limit]
        print(f"Limiting to first {limit} events")
    
    print(f"Found {len(events)} events to import")
    
    with session_scope() as db:
        importer = EventsImporter(db)
        imported = 0
        updated = 0
        
        for i, event in enumerate(events, 1):
            try:
                from app.db.models.models import Event as EventModel
                existing = db.query(EventModel).filter_by(url=event.url).first()
                was_existing = existing is not None
                
                importer.upsert(event)
                
                if was_existing:
                    updated += 1
                    print(f"[{i}/{len(events)}] Updated: {event.title}")
                else:
                    imported += 1
                    print(f"[{i}/{len(events)}] Imported: {event.title}")
            except Exception as e:
                print(f"[{i}/{len(events)}] Error importing {event.title}: {e}")
                continue
        
        print(f"\n✅ Events import complete: {imported} imported, {updated} updated")
    
    return events


def import_fighters():
    """Import all fighters from ufcstats."""
    print("=" * 60)
    print("Importing Fighters from UFCStats")
    print("=" * 60)
    
    scraper = UFCStatsFighterScraper()
    fighters = scraper.get_all_fighters()
    
    print(f"Found {len(fighters)} fighters to import")
    
    with session_scope() as db:
        importer = FightersImporter(db)
        imported = 0
        updated = 0
        
        for i, fighter in enumerate(fighters, 1):
            try:
                from app.db.models.models import Fighter as FighterModel
                existing = db.query(FighterModel).filter_by(url=fighter.url).first()
                was_existing = existing is not None
                
                importer.upsert(fighter)
                
                if was_existing:
                    updated += 1
                else:
                    imported += 1
                
                if i % 100 == 0:
                    print(f"[{i}/{len(fighters)}] Processed: {imported} imported, {updated} updated")
            except Exception as e:
                print(f"[{i}/{len(fighters)}] Error importing {fighter.name}: {e}")
                continue
        
        print(f"\n✅ Fighters import complete: {imported} imported, {updated} updated")
    
    return fighters


def import_fights_for_event(event_url: str):
    """Import fights for a specific event."""
    print("=" * 60)
    print(f"Importing Fights for Event: {event_url}")
    print("=" * 60)
    
    scraper = UFCStatsFightScraper(event_url)
    fights = scraper.get_fights()
    
    print(f"Found {len(fights)} fights to import")
    
    if not fights:
        print("No fights found for this event")
        return []
    
    with session_scope() as db:
        importer = FightsImporter(db)
        imported = 0
        updated = 0
        
        for i, fight in enumerate(fights, 1):
            try:
                importer.upsert(fight)
                imported += 1
                print(f"[{i}/{len(fights)}] Imported fight #{fight.match_number}: {fight.weight_class or 'Unknown weight class'}")
            except ValueError as e:
                print(f"[{i}/{len(fights)}] Skipping fight #{fight.match_number}: {e}")
                continue
            except Exception as e:
                print(f"[{i}/{len(fights)}] Error importing fight #{fight.match_number}: {e}")
                continue
        
        print(f"\n✅ Fights import complete: {imported} imported, {updated} updated")
    
    return fights


def import_fights_for_all_events(limit: Optional[int] = None):
    """Import fights for all events in the database."""
    print("=" * 60)
    print("Importing Fights for All Events")
    print("=" * 60)
    
    from app.db.models.models import Event as EventModel
    
    with session_scope() as db:
        events = db.query(EventModel).all()
        
        if limit:
            events = events[:limit]
            print(f"Limiting to first {limit} events")
        
        print(f"Found {len(events)} events in database")
        
        total_fights = 0
        for i, event in enumerate(events, 1):
            print(f"\n[{i}/{len(events)}] Processing event: {event.title}")
            try:
                fights = import_fights_for_event(event.url)
                total_fights += len(fights)
            except Exception as e:
                print(f"Error processing event {event.title}: {e}")
                continue
        
        print(f"\n✅ Total fights imported: {total_fights}")


def main():
    parser = argparse.ArgumentParser(
        description="Import events, fights, and fighters from ufcstats.com"
    )
    parser.add_argument(
        "--events-only",
        action="store_true",
        help="Import only events"
    )
    parser.add_argument(
        "--fighters-only",
        action="store_true",
        help="Import only fighters"
    )
    parser.add_argument(
        "--fights-only",
        action="store_true",
        help="Import only fights"
    )
    parser.add_argument(
        "--event-url",
        type=str,
        help="Specific event URL to import fights for (requires --fights-only)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of items to import"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.fights_only and args.event_url:
        import_fights_for_event(args.event_url)
        return
    
    if args.fights_only:
        import_fights_for_all_events(args.limit)
        return
    
    if args.events_only:
        import_events(args.limit)
        return
    
    if args.fighters_only:
        import_fighters()
        return
    
    # Import everything
    print("Importing all data from UFCStats...")
    print("This may take a while.\n")
    
    # Step 1: Import events
    events = import_events(args.limit)
    print("\n")
    
    # Step 2: Import fighters (required before importing fights)
    print("Importing fighters (required before importing fights)...")
    import_fighters()
    print("\n")
    
    # Step 3: Import fights for all events
    print("Importing fights for all events...")
    import_fights_for_all_events(args.limit)
    
    print("\n" + "=" * 60)
    print("✅ All imports complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

