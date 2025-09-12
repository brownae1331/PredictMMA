from app.common.celery import celery_app
from app.db.database import sessionLocal
from app.services.importers.events import EventsImporter
from app.services.importers.fighters import FightersImporter
from app.services.importers.fights import FightsImporter
from app.services.importers.rankings import RankingsImporter
from app.schemas.sherdog_schemas import Event as EventSchema, Fight as FightSchema, Fighter as FighterSchema
from app.services.scrapers.ufc_ranking_scraper import UFCRankingScraper
from app.services.scrapers.ufc_sherdog_scraper import UFCSherdogScraper
from celery import group, chord
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta


@contextmanager
def session_scope():
    db = sessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name="sync_all_ufc_events")
def sync_all_ufc_events(self):
    """
    Fetches and imports all UFC events (both upcoming and previous).
    Schedules import tasks for each event.
    """
    scraper = UFCSherdogScraper()

    previous_events: list[EventSchema] = scraper.get_previous_ufc_events()
    upcoming_events: list[EventSchema] = scraper.get_upcoming_ufc_events()

    seen_upcoming_urls: set[str] = {e.url for e in upcoming_events}
    previous_events = [e for e in previous_events if e.url not in seen_upcoming_urls]

    jobs = []
    for event in upcoming_events:
        jobs.append(import_event.s(event.model_dump(mode="json"), is_upcoming=True).set(queue="db"))
    for event in previous_events:
        jobs.append(import_event.s(event.model_dump(mode="json"), is_upcoming=False).set(queue="db"))

    if not jobs:
        return {"status": "no_events"}

    chord_result = chord(jobs)(import_rankings.s().set(queue="db", countdown=60))
    print(f"Scheduled {len(jobs)} event import tasks with delayed chord rankings import")

    return {"status": "scheduled", "num_events": len(jobs), "job_id": chord_result.id}

@celery_app.task(bind=True, name="sync_recent_ufc_events")
def sync_recent_ufc_events(self):
    """
    Syncs upcoming events and previous events from the past 30 days only.
    """
    scraper = UFCSherdogScraper()
        
    previous_events: list[EventSchema] = scraper.get_previous_ufc_events()
    upcoming_events: list[EventSchema] = scraper.get_upcoming_ufc_events()
    
    recent_previous_events = [
        event for event in previous_events 
        if event.date.replace(tzinfo=timezone.utc) >= datetime.now(timezone.utc)-timedelta(days=30)
    ]
    
    seen_upcoming_urls: set[str] = {e.url for e in upcoming_events}
    recent_previous_events = [e for e in recent_previous_events if e.url not in seen_upcoming_urls]

    jobs = []
    for event in upcoming_events:
        jobs.append(import_event.s(event.model_dump(mode="json"), is_upcoming=True).set(queue="db"))
    for event in recent_previous_events:
        jobs.append(import_event.s(event.model_dump(mode="json"), is_upcoming=False).set(queue="db"))
    
    if not jobs:
        print("No recent events found to import")
        return {"status": "no_events"}

    chord_result = chord(jobs)(import_rankings.s().set(queue="db", countdown=60))
    print(f"Scheduled {len(jobs)} recent event import tasks with delayed chord rankings import")
    
    return {"status": "scheduled", "num_events": len(jobs), "job_id": chord_result.id}

@celery_app.task(bind=True, name="import_event")
def import_event(self, event: dict, is_upcoming: bool):
    """
    Upsert the event.
    Delegate scraping of the event's fights to the scrape queue.
    """
    with session_scope() as db:
        try:
            print(f"Importing event: {event.get('title')}")
            event_importer = EventsImporter(db)
            event_importer.upsert(EventSchema(**event))
            db.commit()
            scrape_event_fights.s(event, is_upcoming).set(queue="scrape").delay()

            return {"event_url": event["url"], "dispatched_scrape": True}
        except Exception as exc:
            print(f"Error importing event: {event['title']}")
            raise self.retry(exc=exc, countdown=min(60 * 2 ** self.request.retries, 3600))

@celery_app.task(bind=True, name="scrape_event_fights", max_retries=3, ignore_result=True)
def scrape_event_fights(self, event: dict, is_upcoming: bool):
    """
    Scrape fights for an event (I/O-bound) and schedule fighter imports (scrape)
    and fight upserts (db) using a chord.
    """
    scraper = UFCSherdogScraper()
    try:
        if is_upcoming:
            fights = scraper.get_upcoming_event_fights(event["url"])
        else:
            fights = scraper.get_previous_event_fights(event["url"])

        if not fights:
            print(f"No fights found for event: {event.get('title')}")
            return {"event_url": event["url"], "num_fights": 0}

        unique_fighter_urls: set[str] = set()
        for f in fights:
            if f.fighter_1_url:
                unique_fighter_urls.add(f.fighter_1_url)
            if f.fighter_2_url:
                unique_fighter_urls.add(f.fighter_2_url)

        header = group(
            import_fighter.s(url).set(queue="scrape") for url in unique_fighter_urls
        )
        body = group(
            upsert_fight.s(f.model_dump(mode="json")).set(queue="db") for f in fights
        )
        chord(header)(body)
        print(
            f"Scheduled {len(unique_fighter_urls)} fighter imports and {len(fights)} fight upserts for event: {event.get('title')}"
        )

        return {"event_url": event["url"], "num_fighters": len(unique_fighter_urls), "num_fights": len(fights)}
    except Exception as exc:
        print(f"Failed to scrape fights for event: {event.get('title')}")
        raise self.retry(exc=exc, countdown=min(60 * 2 ** self.request.retries, 3600))

@celery_app.task(bind=True, name="import_fighter", max_retries=3)
def import_fighter(self, fighter_url: str):
    """
    Scrape fighter stats and upsert the fighter.
    Returns a small dict that identifies the fighter.
    """
    scraper = UFCSherdogScraper()
    with session_scope() as db:
        try:
            print(f"Importing fighter: {fighter_url}")
            fighter = scraper.get_fighter_stats(fighter_url)
            fighter_importer = FightersImporter(db)
            fighter_importer.upsert(fighter)

            return {"fighter_url": fighter_url}
        except Exception as exc:
            print(f"Failed to import fighter: {fighter_url}")
            raise self.retry(exc=exc, countdown=min(60 * 2 ** self.request.retries, 3600))

@celery_app.task(bind=True, name="upsert_fight", max_retries=3, ignore_result=True)
def upsert_fight(self, fighter_results: list[dict], fight: dict):
    """
    After the fighters have been imported, upsert the fight itself.
    fighter_results is a list of the return values from import_fighter tasks (in order).
    """
    with session_scope() as db:
        try:
            print(f"Upserting fight: {fight.get('fighter_1_url')} vs {fight.get('fighter_2_url')}")
            fight_importer = FightsImporter(db)
            fight_importer.upsert(FightSchema(**fight))

            return {"fight_url": fight.get("url")}
        except Exception as exc:
            print(f"Failed to upsert fight: {fight.get('fighter_1_url')} vs {fight.get('fighter_2_url')}")
            raise self.retry(exc=exc, countdown=min(30 * 2 ** self.request.retries, 600))

@celery_app.task(bind=True, name="import_fight", max_retries=3, ignore_result=True)
def import_fight(self, fight: dict):
    """
    Spawn two import_fighter tasks in parallel using a chord.
    When both fighters are imported, run upsert_fight.
    """
    fighter_1_url = fight.get("fighter_1_url")
    fighter_2_url = fight.get("fighter_2_url")

    try:
        chord([import_fighter.s(fighter_1_url), import_fighter.s(fighter_2_url)])(upsert_fight.s(fight))
        return {"scheduled": True, "fight_url": fight.get("url")}
    except Exception as exc:
        print(f"Failed to schedule import_fighter tasks for fight {fight.get('url')}")
        raise self.retry(exc=exc, countdown=min(30 * 2 ** self.request.retries, 600))

@celery_app.task(bind=True, name="import_rankings", max_retries=10, ignore_result=True)
def import_rankings(self, *args, **kwargs):
    """
    Fetch and apply UFC rankings.
    When used as a chord callback, receives results from all header tasks but ignores them.
    """
    scraper = UFCRankingScraper()
    with session_scope() as db:
        try:
            print(f"🏆 Starting rankings import")
            rankings = scraper.get_ufc_rankings()
            rankings_importer = RankingsImporter(db)
            rankings_importer.apply_rankings(rankings)
            print(f"✅ Rankings import task completed successfully")
            return {"status": "ok"}
        except Exception as exc:
            print(f"❌ Failed to import rankings: {exc}")
            raise self.retry(exc=exc, countdown=min(60 * 2 ** self.request.retries, 3600))