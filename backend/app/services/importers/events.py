from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models.models import Event as EventModel
from app.schemas.sherdog_schemas import Event as EventSchema

class EventsImporter:
    """
    Class for importing events.
    """

    def __init__(self, db: Session):
        self.db = db

    def upsert(self, event: EventSchema) -> EventModel:
        existing = (
            self.db.query(EventModel)
            .filter_by(url=event.url)
            .first()
        )
        if not existing:
            existing = (
                self.db.query(EventModel)
                .filter_by(
                    date=event.date,
                    location=event.location,
                    organizer=event.organizer,
                )
                .first()
            )
        if existing:
            existing.title = event.title
            existing.date = event.date
            existing.location = event.location
            existing.organizer = event.organizer
            existing.last_updated_at = datetime.now()
            return existing
        
        new_event = EventModel(
            url=event.url,
            title=event.title,
            date=event.date,
            location=event.location,
            organizer=event.organizer,
            last_updated_at=datetime.now(),
        )
        self.db.add(new_event)
        self.db.flush()
        return new_event