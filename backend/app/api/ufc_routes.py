from fastapi import APIRouter
from app.services.ufc_scraper import UFCScraper
from app.schemas.ufc_schemas import Event, EventSummary, Fight, MainEvent
from typing import List

router = APIRouter()
scraper = UFCScraper()

@router.get("/events/links/upcoming")
def get_upcoming_events_links() -> List[str]:
    """
    Get upcoming UFC events links.
    """
    try:
        upcoming_events = scraper.get_upcoming_event_links()
        return upcoming_events
    except Exception as e:
        print(f"Error in get_upcoming_events_links: {e}")
        return {"error": str(e)}

@router.get("/event")
def get_event(event_url: str) -> Event:
    """
    Get a UFC event.
    """
    try:
        event = scraper.get_event_data(event_url)
        return event
    except Exception as e:
        print(f"Error in get_event: {e}")#
        return {"error": str(e)}

@router.get("/event/summary")
def get_event_summary(event_url: str) -> EventSummary:
    """
    Get a summary of a UFC event.
    """
    try:
        print("event_url", event_url)
        event_summary = scraper.get_event_summary_data(event_url)
        return event_summary
    except Exception as e:
        print(f"Error in get_event_summary: {e}")
        return {"error": str(e)}
    
@router.get("/event/fights")
def get_event_fights(event_url: str) -> List[Fight]:
    """
    Get the fights of a UFC event.
    """
    try:
        fights = scraper.get_fight_data(event_url)
        if fights is None:
            return []
        return fights
    except Exception as e:
        print(f"Error in get_event_fights: {e}")
        return {"error": str(e)}
    
@router.get("/event/main-event")
def get_event_main_event(event_url: str) -> MainEvent:
    """
    Get the main event of a UFC event.
    """
    try:
        main_event = scraper.get_main_event_data(event_url)
        if main_event is None:
            return {"error": "No main event found"}
        return main_event
    except Exception as e:
        print(f"Error in get_event_main_event: {e}")
        return {"error": str(e)}