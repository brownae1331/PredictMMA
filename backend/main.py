from fastapi import FastAPI
from ufc_scraper import UFCEventsScraper

app = FastAPI()

@app.get("/")
def read_root():
    scraper = UFCEventsScraper()
    events = scraper.get_upcoming_event_links()
    # fights = scraper.get_fight_data(events[0])
    return events
