from app.common.celery import celery_app
from app.db.database import sessionLocal
from app.services.importers.events import EventsImporter
from app.services.importers.fighters import FightersImporter
from app.services.importers.fights import FightsImporter
from app.services.importers.rankings import RankingsImporter
from app.schemas.sherdog_schemas import Event as EventSchema, Fight as FightSchema, Fighter as FighterSchema
from app.services.scrapers.ufc_ranking_scraper import UFCRankingScraper

def _session():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

@celery_app.task(name="tasks.imports.upsert_event")
def upsert_event(event: dict) -> None:
    event_model = EventSchema.model_validate(event)
    print("[Celery] upsert_event START", event_model.title)
    db = next(_session())
    EventsImporter(db).upsert(event_model)
    db.commit()
    print("[Celery] upsert_event DONE", event_model.title)

@celery_app.task(name="tasks.imports.upsert_fighter")
def upsert_fighter(fighter: dict) -> None:
    fighter_model = FighterSchema.model_validate(fighter)
    print("[Celery] upsert_fighter START", fighter_model.name)
    db = next(_session())
    FightersImporter(db).upsert(fighter_model)
    db.commit()
    print("[Celery] upsert_fighter DONE", fighter_model.name)

@celery_app.task(name="tasks.imports.upsert_fight")
def upsert_fight(fight: dict) -> None:
    fight_model = FightSchema.model_validate(fight)
    print("[Celery] upsert_fight START", fight_model.event_url, fight_model.match_number)
    db = next(_session())
    FightsImporter(db).upsert(fight_model)
    db.commit()
    print("[Celery] upsert_fight DONE", fight_model.event_url, fight_model.match_number)

@celery_app.task(name="tasks.imports.apply_rankings")
def apply_rankings() -> None:
    print("[Celery] apply_rankings START")
    db = next(_session())
    rankings = UFCRankingScraper().get_ufc_rankings()
    RankingsImporter(db).apply_rankings(rankings)
    db.commit()
    print("[Celery] apply_rankings DONE")