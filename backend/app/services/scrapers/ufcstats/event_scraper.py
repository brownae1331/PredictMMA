import sys
from pathlib import Path

# Add backend directory to path so imports work when running as script
backend_dir = Path(__file__).parent.parent.parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from app.schemas.scraper_schemas import Event

class UFCStatsEventScraper:
    def __init__(self):
        self.base_url = "http://ufcstats.com/statistics/events/"
        self.scraper = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }

    def parse_events_from_page(self, page_path: str) -> list[Event]:
        url = urljoin(self.base_url, page_path)
        response = self.scraper.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        events = []
        event_containers = soup.find_all("tr", class_="b-statistics__table-row")
        for event in event_containers:
            left_container = event.find("td", class_="b-statistics__table-col")
            if not left_container:
                continue
            right_container = event.find("td", class_="b-statistics__table-col b-statistics__table-col_style_big-top-padding")
            if not right_container:
                continue

            url = left_container.find("a")["href"]
            title = left_container.find("a").text.strip()
            date_str = left_container.find("span", class_="b-statistics__date").text.strip()
            date = datetime.strptime(date_str, "%B %d, %Y")
            location = right_container.get_text(strip=True)
            
            events.append(Event(
                url=url,
                title=title,
                date=date,
                location=location,
                organizer="UFC",
            ))

        return events

    def get_ufc_1(self) -> Event:
        """Doesn't show up in the completed events page, so we need to add it manually."""
        return Event(
            url="http://ufcstats.com/event-details/6420efac0578988b",
            title="UFC 1: The Beginning",
            date=datetime(1993, 11, 12),
            location="Denver, Colorado, USA",
            organizer="UFC",
        )

    def get_all_events(self) -> list[Event]:
        events = self.parse_events_from_page("completed?page=all")
        events.extend(self.parse_events_from_page("upcoming?page=all"))
        events.append(self.get_ufc_1())
        return events


ufc = UFCStatsEventScraper()
print(ufc.get_all_events())