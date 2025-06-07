from fastapi import APIRouter
from app.services.ufc_scraper import UFCScraper, Event
from typing import Optional, List
from fastapi import Query

router = APIRouter()

@router.get("/events/upcoming")
def get_upcoming_events(limit: Optional[int] = Query(None, gt=0)) -> List[Event]:
    """
    Get upcoming UFC events.
    Optional query parameter 'limit' to restrict number of events returned.
    """
    try:
        scraper = UFCScraper()
        upcoming_events = scraper.get_upcoming_event_links()

        if not upcoming_events:
            return []

        if limit:
            upcoming_events = upcoming_events[:limit]

        events_data = []
        for event_link in upcoming_events:
            event_data = scraper.get_event_data(event_link)
            events_data.append(event_data)

        return events_data

    except Exception as e:
        print(f"Error in get_upcoming_events: {e}")
        return {"error": str(e)}