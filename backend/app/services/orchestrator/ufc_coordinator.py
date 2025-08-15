from sqlalchemy.orm import Session
from celery import chain, group, chord
from app.services.scrapers.ufc_sherdog_scraper import UFCSherdogScraper
from app.services.scrapers.ufc_ranking_scraper import UFCRankingScraper
from app.services.importers.events import EventsImporter
from app.services.importers.fights import FightsImporter
from app.services.importers.fighters import FightersImporter
from app.services.importers.rankings import RankingsImporter
from app.schemas.sherdog_schemas import Event as EventSchema, Fight as FightSchema, Fighter as FighterSchema
from app.tasks.tasks import (
    upsert_event,
    upsert_fighter,
    upsert_fight,
    apply_rankings,
)

class UFCScraperCoordinator:
    """
    Class for coordinating the scraping and importing of UFC data.
    """
    def __init__(self):
        self.sherdog_scraper = UFCSherdogScraper()
        self.ufc_ranking_scraper = UFCRankingScraper()
    
    def sync_ufc_data(self, db: Session) -> None:
        """
        Syncs the UFC data from the scrapers and imports it into the database.
        """
        previous_events: list[EventSchema] = self.sherdog_scraper.get_previous_ufc_events()
        upcoming_events: list[EventSchema] = self.sherdog_scraper.get_upcoming_ufc_events()

        seen_upcoming_urls: set[str] = set()
        unique_upcoming_events: list[EventSchema] = []
        for event in upcoming_events:
            if event.url in seen_upcoming_urls:
                continue
            seen_upcoming_urls.add(event.url)
            unique_upcoming_events.append(event)
        upcoming_events = unique_upcoming_events

        previous_events = [e for e in previous_events if e.url not in seen_upcoming_urls]

        for event in upcoming_events:
            print(f"Importing upcoming event: {event.title}")
            event_importer = EventsImporter(db)
            event_importer.upsert(event)

            fights: list[FightSchema] = self.sherdog_scraper.get_upcoming_event_fights(event.url)
            for fight in fights:
                print(f"Importing upcoming fight: {fight.fighter_1_url} vs {fight.fighter_2_url}")
                fighter_1: FighterSchema = self.sherdog_scraper.get_fighter_stats(fight.fighter_1_url)
                fighter_2: FighterSchema = self.sherdog_scraper.get_fighter_stats(fight.fighter_2_url)

                fighter_1_importer = FightersImporter(db)
                fighter_1_importer.upsert(fighter_1)

                fighter_2_importer = FightersImporter(db)
                fighter_2_importer.upsert(fighter_2)

                fight_importer = FightsImporter(db)
                fight_importer.upsert(fight)
            db.commit()

        for event in previous_events:
            print(f"Importing previous event: {event.title}")
            event_importer = EventsImporter(db)
            event_importer.upsert(event)

            fights: list[FightSchema] = self.sherdog_scraper.get_previous_event_fights(event.url)
            for fight in fights:
                print(f"Importing previous fight: {fight.fighter_1_url} vs {fight.fighter_2_url}")
                fighter_1: FighterSchema = self.sherdog_scraper.get_fighter_stats(fight.fighter_1_url)
                fighter_2: FighterSchema = self.sherdog_scraper.get_fighter_stats(fight.fighter_2_url)

                fighter_1_importer = FightersImporter(db)
                fighter_1_importer.upsert(fighter_1)

                fighter_2_importer = FightersImporter(db)
                fighter_2_importer.upsert(fighter_2)

                fight_importer = FightsImporter(db)
                fight_importer.upsert(fight)
            db.commit()

        print("Importing rankings")
        rankings = self.ufc_ranking_scraper.get_ufc_rankings()
        rankings_importer = RankingsImporter(db)
        rankings_importer.apply_rankings(rankings)
        db.commit()

    def schedule_sync_ufc_data(self) -> str:
        """
        Build and dispatch a Celery DAG to sync UFC data in parallel while enforcing:
        - Event upsert before fights of that event
        - Both fighters upserted before their fight
        - Rankings applied once after all events/fights complete
        Returns the Celery result id for tracking.
        """
        previous_events: list[EventSchema] = self.sherdog_scraper.get_previous_ufc_events()
        upcoming_events: list[EventSchema] = self.sherdog_scraper.get_upcoming_ufc_events()

        seen_upcoming_urls: set[str] = {e.url for e in upcoming_events}
        previous_events = [e for e in previous_events if e.url not in seen_upcoming_urls]
        all_events: list[EventSchema] = upcoming_events + previous_events

        def fight_workflow(fight: FightSchema):
            print(f"Scheduling fight: {fight.fighter_1_url} vs {fight.fighter_2_url}")
            fighter_1: FighterSchema = self.sherdog_scraper.get_fighter_stats(fight.fighter_1_url)
            fighter_2: FighterSchema = self.sherdog_scraper.get_fighter_stats(fight.fighter_2_url)

            fighters_group = group(
                upsert_fighter.si(fighter=fighter_1.model_dump(mode="json")),
                upsert_fighter.si(fighter=fighter_2.model_dump(mode="json")),
            )
            return chain(
                fighters_group,
                upsert_fight.si(fight=fight.model_dump(mode="json")),
            )

        def event_workflow(event: EventSchema):
            print(f"Scheduling event: {event.title}")
            if event.url in seen_upcoming_urls:
                fights: list[FightSchema] = self.sherdog_scraper.get_upcoming_event_fights(event.url)
            else:
                fights = self.sherdog_scraper.get_previous_event_fights(event.url)

            per_fight_chains = [fight_workflow(f) for f in fights]
            if per_fight_chains:
                return chain(
                    upsert_event.si(event=event.model_dump(mode="json")),
                    group(per_fight_chains),
                )
            else:
                return upsert_event.si(event=event.model_dump(mode="json"))

        header = group([event_workflow(e) for e in all_events])
        result = chord(header)(apply_rankings.si())
        return result.id

    def test_task(self):
        upcoming_events = self.sherdog_scraper.get_upcoming_ufc_events()
        print(upcoming_events)
        # return upsert_event.delay(event=upcoming_events[0].model_dump(mode="json")).id