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
def upsert_event(event_dict: dict) -> None:
    print("[Celery] upsert_event START", event_dict.get("title"))
    db = next(_session())
    EventsImporter(db).upsert(EventSchema(**event_dict))
    db.commit()
    print("[Celery] upsert_event DONE", event_dict.get("title"))

@celery_app.task(name="tasks.imports.upsert_fighter")
def upsert_fighter_task(fighter_dict: dict) -> None:
    print("[Celery] upsert_fighter START", fighter_dict.get("name"))
    db = next(_session())
    FightersImporter(db).upsert(FighterSchema(**fighter_dict))
    db.commit()
    print("[Celery] upsert_fighter DONE", fighter_dict.get("name"))

@celery_app.task(name="tasks.imports.upsert_fight")
def upsert_fight_task(fight_dict: dict) -> None:
    print("[Celery] upsert_fight START", fight_dict.get("event_url"), fight_dict.get("match_number"))
    db = next(_session())
    FightsImporter(db).upsert(FightSchema(**fight_dict))
    db.commit()
    print("[Celery] upsert_fight DONE", fight_dict.get("event_url"), fight_dict.get("match_number"))

@celery_app.task(name="tasks.imports.apply_rankings")
def apply_rankings_task() -> None:
    print("[Celery] apply_rankings START")
    db = next(_session())
    rankings = UFCRankingScraper().get_ufc_rankings()
    RankingsImporter(db).apply_rankings(rankings)
    db.commit()
    print("[Celery] apply_rankings DONE")