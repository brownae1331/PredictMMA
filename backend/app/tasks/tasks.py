from app.common.celery import celery_app
from app.db.database import sessionLocal
from app.services.importers.events import EventsImporter
from app.services.importers.fighters import FightersImporter
from app.services.importers.fights import FightsImporter
from app.services.importers.rankings import RankingsImporter
from app.schemas.sherdog_schemas import Event as EventSchema, Fight as FightSchema, Fighter as FighterSchema
from app.services.scrapers.ufc_ranking_scraper import UFCRankingScraper
from app.services.scrapers.ufc_sherdog_scraper import UFCSherdogScraper
from celery import group


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


@celery_app.task(
    name="tasks.imports.process_fight",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def process_fight(self, fight: dict) -> None:
    """
    Scrape both fighters for the given fight, upsert fighters first, then upsert the fight.
    Ensures ordering: fighters -> fight. Assumes the event has already been upserted.
    Retries automatically on transient scraper/network errors.
    """
    fight_model = FightSchema.model_validate(fight)
    print(
        "[Celery] process_fight START",
        fight_model.event_url,
        fight_model.match_number,
        fight_model.fighter_1_url,
        fight_model.fighter_2_url,
    )

    scraper = UFCSherdogScraper()

    fighter_1: FighterSchema = scraper.get_fighter_stats(fight_model.fighter_1_url)
    fighter_2: FighterSchema = scraper.get_fighter_stats(fight_model.fighter_2_url)

    db = next(_session())

    FightersImporter(db).upsert(fighter_1)
    FightersImporter(db).upsert(fighter_2)
    db.commit()

    FightsImporter(db).upsert(fight_model)
    db.commit()

    print("[Celery] process_fight DONE", fight_model.event_url, fight_model.match_number)


@celery_app.task(
    name="tasks.imports.process_event",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def process_event(self, event: dict, is_upcoming: bool) -> None:
    """
    Upsert the event, scrape its fights on the worker, and process all fights in parallel.
    """
    event_model = EventSchema.model_validate(event)
    print("[Celery] process_event START", event_model.title)

    db = next(_session())
    EventsImporter(db).upsert(event_model)
    db.commit()

    scraper = UFCSherdogScraper()
    try:
        if is_upcoming:
            fights: list[FightSchema] = scraper.get_upcoming_event_fights(event_model.url)
        else:
            fights = scraper.get_previous_event_fights(event_model.url)
    except Exception as exc:
        print("[Celery] process_event fights fetch failed", event_model.title, exc)
        fights = []

    if fights:
        job = group([process_fight.s(fight=f.model_dump(mode="json")) for f in fights])
        job.apply_async()

    print("[Celery] process_event DONE", event_model.title)