from sqlalchemy.orm import Session

from app.schemas.sherdog_schemas import Event as EventSchema
from app.db.models.models import Event as EventModel


def upsert_events(events: list[EventSchema], db: Session) -> None:
    """Insert events into the database if they don't already exist.

    Args:
        events: List of EventSchema objects scraped from Sherdog.
        db: SQLAlchemy session.
    """
    for event in events:
        # Avoid duplicate entries by checking for existing record via primary key.
        exists = db.query(EventModel).filter_by(event_url=event.event_url).first()
        if exists:
            continue

        db_event = EventModel(
            event_url=event.event_url,
            event_title=event.event_title,
            event_date=event.event_date,
            event_location=event.event_location,
            event_organizer=event.event_organizer,
        )
        db.add(db_event)

    db.commit() 