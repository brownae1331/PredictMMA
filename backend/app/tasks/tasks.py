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


def _session():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

@celery_app.task(bind=True, name="sync_ufc_data")
def sync_ufc_data(self):
    """
    Fetches upcoming and previous UFC events.
    Schedules import tasks for each event.
    """
    scraper = UFCSherdogScraper()

    previous_events: list[EventSchema] = scraper.get_previous_ufc_events()
    upcoming_events: list[EventSchema] = scraper.get_upcoming_ufc_events()

    seen_upcoming_urls: set[str] = {e.url for e in upcoming_events}
    previous_events = [e for e in previous_events if e.url not in seen_upcoming_urls]

    jobs = []
    for event in upcoming_events:
        jobs.append(import_event.s(event.model_dump(mode="json"), is_upcoming=True))
    for event in previous_events:
        jobs.append(import_event.s(event.model_dump(mode="json"), is_upcoming=False))

    if not jobs:
        print("No events found to import")
        return {"status": "no_events"}

    group_result = group(jobs).apply_async()
    print(f"Scheduled {len(jobs)} event import tasks")

    import_rankings.apply_async()

    return {"status": "scheduled", "num_events": len(jobs), "job_id": group_result.id}

@celery_app.task(bind=True, name="import_event")
def import_event(self, event: dict, is_upcoming: bool):
    """
    Upsert the event.
    Scrape the event's fights.
    Schedule each fight import in parallel.
    """
    scraper = UFCSherdogScraper()
    db = next(_session())
    try:
        print(f"Importing event: {event.get('title')}")
        event_importer = EventsImporter(db)
        event_importer.upsert(EventSchema(**event))

        if is_upcoming:
            fights = scraper.get_upcoming_event_fights(event["url"])
        else:
            fights = scraper.get_previous_event_fights(event["url"])

        if fights:
            job = group(import_fight.s(f.model_dump(mode="json")) for f in fights).apply_async()
            print(f"Scheduled {len(fights)} fight import imports for event: {event['title']}")
        else:
            print(f"No fights found for event: {event['title']}")
        
        return {"event_url": event["url"], "num_fights": len(fights)}
    except Exception as exc:
        print(f"Error importing event: {event['title']}")
        raise self.retry(exc=exc, countdown=min(60 * 2 ** self.request.retries, 3600))

@celery_app.task(bind=True, name="import_fighter", max_retries=3)
def import_fighter(self, fighter_url: str):
    """
    Scrape fighter stats and upsert the fighter.
    Returns a small dict that identifies the fighter.
    """
    db = next(_session())
    scraper = UFCSherdogScraper()
    try:
        print(f"Importing fighter: {fighter_url}")
        fighter = scraper.get_fighter_stats(fighter_url)
        fighter_importer = FightersImporter(db)
        fighter_importer.upsert(fighter)

        db.commit()
        return {"fighter_url": fighter_url}
    except Exception as exc:
        print(f"Failed to import fighter: {fighter_url}")
        raise self.retry(exc=exc, countdown=min(60 * 2 ** self.request.retries, 3600))

@celery_app.task(bind=True, name="upsert_fight", max_retries=3)
def upsert_fight(self, fighter_results: list[dict], fight: dict):
    """
    After the fighters have been imported, upsert the fight itself.
    fighter_results is a list of the return values from import_fighter tasks (in order).
    """
    db = next(_session())
    try:
        print(f"Upserting fight: {fight.get('fighter_1_url')} vs {fight.get('fighter_2_url')}")
        fight_importer = FightsImporter(db)
        fight_importer.upsert(FightSchema(**fight))

        db.commit()
        return {"fight_url": fight.get("url")}
    except Exception as exc:
        print(f"Failed to upsert fight: {fight.get('fighter_1_url')} vs {fight.get('fighter_2_url')}")
        raise self.retry(exc=exc, countdown=min(30 * 2 ** self.request.retries, 600))

@celery_app.task(bind=True, name="import_fight", max_retries=3)
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

@celery_app.task(bind=True, name="import_rankings", max_retries=3)
def import_rankings(self):
    """
    Fetch and apply UFC rankings.
    """
    db = next(_session())
    scraper = UFCRankingScraper()
    try:
        print("Importing rankings")
        rankings = scraper.get_ufc_rankings()
        rankings_importer = RankingsImporter(db)
        rankings_importer.apply_rankings(rankings)
        db.commit()
        return {"status": "ok"}
    except Exception as exc:
        print("Failed to import rankings")
        raise self.retry(exc=exc, countdown=min(60 * 2 ** self.request.retries, 3600))