from app.common.celery import celery_app
from app.db.database import sessionLocal
from app.services.importers.events import EventsImporter
from app.services.importers.fighters import FightersImporter
from app.services.importers.fights import FightsImporter
from app.services.importers.rankings import RankingsImporter
from app.schemas.sherdog_schemas import Event as EventSchema, Fight as FightSchema, Fighter as FighterSchema
from app.services.scrapers.ufc_ranking_scraper import UFCRankingScraper

@celery_app.task(name="tasks.debug.ping")
def debug_ping(message: str = "ping") -> str:
    print(f"debug_ping: {message}")
    return "pong"

def _session():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

@celery_app.task(name="tasks.imports.upsert_event")
def upsert_event(event: EventSchema) -> None:
    print("[Celery] upsert_event START", event.title)
    db = next(_session())
    EventsImporter(db).upsert(event)
    db.commit()
    print("[Celery] upsert_event DONE", event.title)

@celery_app.task(name="tasks.imports.upsert_fighter")
def upsert_fighter_task(fighter: FighterSchema) -> None:
    print("[Celery] upsert_fighter START", fighter.name)
    db = next(_session())
    FightersImporter(db).upsert(fighter)
    db.commit()
    print("[Celery] upsert_fighter DONE", fighter.name)

@celery_app.task(name="tasks.imports.upsert_fight")
def upsert_fight_task(fight: FightSchema) -> None:
    print("[Celery] upsert_fight START", fight.event_url, fight.match_number)
    db = next(_session())
    FightsImporter(db).upsert(fight)
    db.commit()
    print("[Celery] upsert_fight DONE", fight.event_url, fight.match_number)

@celery_app.task(name="tasks.imports.apply_rankings")
def apply_rankings_task() -> None:
    print("[Celery] apply_rankings START")
    db = next(_session())
    rankings = UFCRankingScraper().get_ufc_rankings()
    RankingsImporter(db).apply_rankings(rankings)
    db.commit()
    print("[Celery] apply_rankings DONE")