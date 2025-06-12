from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.ufc_scraper import UFCScraper
from app.models.ufc_models import Event, EventSummary
from typing import List

router = APIRouter()

@router.get("/event/")
def get_event(event_url: str) -> Event:
    """
    Get a UFC event.
    """
    try:
        scraper = UFCScraper()
        event = scraper.get_event_data(event_url)
        return event
    except Exception as e:
        print(f"Error in get_event: {e}")
        return {"error": str(e)}

@router.get("/event/summary")
def get_event_summary(event_url: str) -> EventSummary:
    """
    Get a summary of a UFC event.
    """
    try:
        print("event_url", event_url)
        scraper = UFCScraper()
        event_summary = scraper.get_event_summary_data(event_url)
        return event_summary
    except Exception as e:
        print(f"Error in get_event_summary: {e}")
        return {"error": str(e)}
    
@router.get("/events/links/upcoming")
def get_upcoming_events_links() -> List[str]:
    """
    Get upcoming UFC events links.
    """
    try:
        scraper = UFCScraper()
        upcoming_events = scraper.get_upcoming_event_links()
        return upcoming_events
    except Exception as e:
        print(f"Error in get_upcoming_events_links: {e}")
        return {"error": str(e)}