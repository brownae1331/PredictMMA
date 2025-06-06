from fastapi import APIRouter
from app.services.ufc_scraper import UFCEventsScraper

router = APIRouter()

@router.get("/upcoming-events")
def get_upcoming_events():
    try:
        scraper = UFCEventsScraper()
        upcoming_events = scraper.get_upcoming_event_links()
        
        if not upcoming_events:
            return []
        
        first_three_events = upcoming_events[:3]
        
        events_data = []
        for event_link in first_three_events:
            event_data = scraper.get_event_data(event_link)
            events_data.append(event_data)
        
        return events_data
    except Exception as e:
        print(f"Error in get_upcoming_events: {e}")
        return {"error": str(e)}

@router.get("/all-upcoming-events")
def get_all_upcoming_events():
    try:
        scraper = UFCEventsScraper()
        upcoming_events = scraper.get_upcoming_event_links()
        
        if not upcoming_events:
            return []
        
        events_data = []
        for event_link in upcoming_events:
            event_data = scraper.get_event_data(event_link)
            events_data.append(event_data)
        
        return events_data
    except Exception as e:
        print(f"Error in get_all_upcoming_events: {e}")
        return {"error": str(e)}