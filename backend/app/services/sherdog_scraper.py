import requests
import cloudscraper
from bs4 import BeautifulSoup
from typing import List
from app.schemas.sherdog_schemas import Event, Fight
from urllib.parse import urljoin
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

class SherdogScraper:
    def __init__(self):
        self.base_url = "https://www.sherdog.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }

    def get_previous_events(self) -> List[Event]:
        """
        Scrapes every previous UFC event from Sherdog.
        Returns a list of events.
        """
        current_url = urljoin(self.base_url, "/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/1")
        events = []
        current_page = 1

        while current_url:
            print(f"Scraping page {current_page}...")
            scraper = cloudscraper.create_scraper()
            response = scraper.get(current_url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")

            events_container = soup.find("div", id="recent_tab")
            for tr in events_container.find_all("tr", itemtype="http://schema.org/Event"):
                event_url = urljoin(self.base_url, tr.find("a", itemprop="url")["href"])
                event_title = tr.find("span", itemprop="name").text.strip()
                
                start_raw  = tr.find("meta", itemprop="startDate")["content"]
                dt = datetime.fromisoformat(start_raw)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                event_date = dt.astimezone(ZoneInfo("Europe/London"))

                location = tr.find("td", itemprop="location").get_text(" ", strip=True)
                
                events.append(Event(
                    event_url=event_url,
                    event_title=event_title,
                    event_date=event_date,
                    event_location=location,
                    event_organizer="UFC",
                ))

            pagination = events_container.find("span", class_="pagination")
            older_link = None
            if pagination:
                for a in pagination.find_all("a"):
                    if "Older Events" in a.text:
                        older_link = urljoin(self.base_url, a["href"])
                        break

            if older_link:
                current_url = older_link
            else:
                current_url = None

            current_page += 1

        return events

    def get_upcoming_events(self) -> List[Event]:
        """
        Scrapes every upcoming UFC event from Sherdog.
        Returns a list of events.
        """
        current_url = urljoin(self.base_url, "/organizations/Ultimate-Fighting-Championship-UFC-2")
        events = []

        scraper = cloudscraper.create_scraper()
        response = scraper.get(current_url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        events_container = soup.find("div", id="upcoming_tab")
        for tr in events_container.find_all("tr", itemtype="http://schema.org/Event"):
            event_url = urljoin(self.base_url, tr.find("a", itemprop="url")["href"])
            event_title = tr.find("span", itemprop="name").text.strip()

            start_raw = tr.find("meta", itemprop="startDate")["content"]
            dt = datetime.fromisoformat(start_raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            event_date = dt.astimezone(ZoneInfo("Europe/London"))

            location = tr.find("td", itemprop="location").get_text(" ", strip=True)

            events.append(Event(
                event_url=event_url,
                event_title=event_title,
                event_date=event_date,
                event_location=location,
                event_organizer="UFC",
            ))
        
        return events
    
    def get_previous_event_fights(self, event_url: str) -> List[Fight]:
        """
        Scrapes the fights for a given previous event from Sherdog.
        Returns a list of fights.
        """
        scraper = cloudscraper.create_scraper()
        response = scraper.get(event_url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        fights = []

        # Some older Sherdog pages may not have a dedicated "main event" container.
        main_event_container = soup.find("div", itemprop="subEvent")
        if main_event_container:
            fighter_1_container = main_event_container.find("div", class_="fighter left_side")
            fighter_2_container = main_event_container.find("div", class_="fighter right_side")

            fighter_1_link_rel = fighter_1_container.find("a", itemprop="url").get("href")
            fighter_2_link_rel = fighter_2_container.find("a", itemprop="url").get("href")

            fighter_1_link = urljoin(self.base_url, fighter_1_link_rel)
            fighter_2_link = urljoin(self.base_url, fighter_2_link_rel)

            fight_weight = main_event_container.find("span", class_="weight_class").text.strip()

            if fighter_1_container.find("span", class_="final_result win"):
                fight_winner = "fighter_1"
            elif fighter_2_container.find("span", class_="final_result win"):
                fight_winner = "fighter_2"
            elif (
                fighter_1_container.find("span", class_="final_result no_contest")
                or fighter_2_container.find("span", class_="final_result no_contest")
            ):
                fight_winner = "no contest"
            else:
                fight_winner = "draw"

            resume_table = main_event_container.find("table", class_="fight_card_resume")
            resume_cells = resume_table.find_all("td")

            fight_idx = int(
                "".join(filter(str.isdigit, resume_cells[0].get_text(strip=True)))
            )
            fight_method = resume_cells[1].get_text(" ", strip=True)
            fight_round = int(
                "".join(filter(str.isdigit, resume_cells[3].get_text(strip=True)))
            )
            fight_time = resume_cells[4].get_text(strip=True)

            fights.append(
                Fight(
                    event_url=event_url,
                    fight_idx=fight_idx,
                    fighter_1_link=fighter_1_link,
                    fighter_2_link=fighter_2_link,
                    fight_weight=fight_weight,
                    fight_winner=fight_winner,
                    fight_method=fight_method,
                    fight_round=fight_round,
                    fight_time=fight_time,
                )
            )

        fight_card_container = soup.find("div", class_="new_table_holder")
        if not fight_card_container:
            return fights

        for tr in fight_card_container.find_all("tr", itemprop="subEvent"):
            tds = tr.find_all("td")

            fight_idx_text = tds[0].get_text(strip=True)
            fight_idx_val = int(''.join(filter(str.isdigit, fight_idx_text)))

            fighter_1_container = tds[1]
            fighter_2_container = tds[3]

            fighter_1_link_rel = fighter_1_container.find("a", itemprop="url")["href"]
            fighter_2_link_rel = fighter_2_container.find("a", itemprop="url")["href"]
            fighter_1_link = urljoin(self.base_url, fighter_1_link_rel)
            fighter_2_link = urljoin(self.base_url, fighter_2_link_rel)

            fight_weight = tds[2].find("span", class_="weight_class").text.strip()

            if fighter_1_container.find("span", class_="final_result win"):
                fight_winner = "fighter_1"
            elif fighter_2_container.find("span", class_="final_result win"):
                fight_winner = "fighter_2"
            elif (fighter_1_container.find("span", class_="final_result no_contest") or
                    fighter_2_container.find("span", class_="final_result no_contest")):
                fight_winner = "no contest"
            else:
                fight_winner = "draw"

            fight_method = tds[4].find("b").get_text(" ", strip=True)

            fight_round_val = int(
                "".join(filter(str.isdigit, tds[5].get_text(strip=True)))
            )

            fight_time = tds[6].get_text(strip=True)

            fights.append(Fight(
                event_url=event_url,
                fight_idx=fight_idx_val,
                fighter_1_link=fighter_1_link,
                fighter_2_link=fighter_2_link,
                fight_weight=fight_weight,
                fight_winner=fight_winner,
                fight_method=fight_method,
                fight_round=fight_round_val,
                fight_time=fight_time,
            ))

        return fights
    
    def get_upcoming_event_fights(self, event_url: str) -> List[Fight]:
        """
        Scrapes the fights for a given upcoming event from Sherdog.
        Returns a list of fights.
        """
        scraper = cloudscraper.create_scraper()
        response = scraper.get(event_url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        fights = []

        fight_card_container = soup.find("div", class_="new_table_holder")
        if fight_card_container:
            for tr in fight_card_container.find_all("tr", itemprop="subEvent"):
                tds = tr.find_all("td")

                fight_idx_text = tds[0].get_text(strip=True)
                fight_idx_val = int(''.join(filter(str.isdigit, fight_idx_text)))

                fighter_1_container = tds[1]
                fighter_2_container = tds[3]

                fighter_1_link_rel = fighter_1_container.find("a", itemprop="url")["href"]
                fighter_2_link_rel = fighter_2_container.find("a", itemprop="url")["href"]
                fighter_1_link = urljoin(self.base_url, fighter_1_link_rel)
                fighter_2_link = urljoin(self.base_url, fighter_2_link_rel)

                fight_weight = tds[2].find("span", class_="weight_class").text.strip()
                
                fights.append(Fight(
                    event_url=event_url,
                    fight_idx=fight_idx_val,
                    fighter_1_link=fighter_1_link,
                    fighter_2_link=fighter_2_link,
                    fight_weight=fight_weight,
                    fight_winner="",
                    fight_method="",
                    fight_round=0,
                    fight_time="",
                ))
            

        main_event_container = soup.find("div", itemprop="subEvent")
        if main_event_container:
            fighter_1_container = main_event_container.find("div", class_="fighter left_side")
            fighter_2_container = main_event_container.find("div", class_="fighter right_side")

            fighter_1_link_rel = fighter_1_container.find("a", itemprop="url").get("href")
            fighter_2_link_rel = fighter_2_container.find("a", itemprop="url").get("href")

            fighter_1_link = urljoin(self.base_url, fighter_1_link_rel)
            fighter_2_link = urljoin(self.base_url, fighter_2_link_rel)

            fight_weight = main_event_container.find("span", class_="weight_class").text.strip()

            fights.append(
                Fight(
                    event_url=event_url,
                    fight_idx=len(fights) + 1,
                    fighter_1_link=fighter_1_link,
                    fighter_2_link=fighter_2_link,
                    fight_weight=fight_weight,
                    fight_winner="",
                    fight_method="",
                    fight_round=0,
                    fight_time="",
                )
            )

        return fights