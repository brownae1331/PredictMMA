import re
import time
import cloudscraper
from bs4 import BeautifulSoup
from typing import List

from app.core.utils.string_utils import strip_accents
from app.schemas.sherdog_schemas import Event, Fight, Fighter
from urllib.parse import urljoin
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dateutil import parser as dateutil_parser

class UFCSherdogScraper:
    """Scraper for UFC events on Sherdog.com."""
    
    UNKNOWN_FIGHTER_URL = "unknown"

    def __init__(self):
        self.base_url = "https://www.sherdog.com"
        # Reuse a single cloudscraper session to persist cookies and mimic a browser more closely
        self.scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        # Realistic headers help reduce chances of a 403 from Cloudflare
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.sherdog.com/",
        }

    def _get(self, url: str, max_retries: int = 3):
        """GET with simple retry/backoff and cookie warm-up for Cloudflare blocks."""
        last_exc: Exception | None = None
        for attempt in range(max_retries):
            try:
                response = self.scraper.get(url, headers=self.headers, timeout=30)
                # If Cloudflare blocks (403) or we are being rate-limited (429), warm up cookies and retry
                if response.status_code in (403, 429):
                    try:
                        # Visit base page to obtain/refresh cookies
                        self.scraper.get(self.base_url + "/", headers=self.headers, timeout=30)
                    except Exception:
                        pass
                    # Backoff and rotate the scraper session to refresh any tokens
                    time.sleep(1.5 * (attempt + 1))
                    self.scraper = cloudscraper.create_scraper(
                        browser={"browser": "chrome", "platform": "windows", "mobile": False}
                    )
                    continue
                response.raise_for_status()
                return response
            except Exception as exc:
                last_exc = exc
                time.sleep(1.5 * (attempt + 1))
                # Recreate session on generic network errors
                self.scraper = cloudscraper.create_scraper(
                    browser={"browser": "chrome", "platform": "windows", "mobile": False}
                )
        # Exhausted retries
        if last_exc:
            raise last_exc
        raise Exception("Request failed with no further detail")

    @staticmethod
    def _is_valid_href(href: str) -> bool:
        """Return True if the href looks like a real link to a fighter profile."""
        if not href:
            return False
        return not href.strip().lower().startswith("javascript:")

    def get_previous_ufc_events(self) -> List[Event]:
        """
        Scrapes every previous UFC event from Sherdog.
        Returns a list of events.
        """
        current_url = urljoin(self.base_url, "/organizations/Ultimate-Fighting-Championship-UFC-2/recent-events/1")
        events = []
        current_page = 1

        while current_url:
            print(f"Scraping page {current_page}...")
            try:
                response = self._get(current_url)
            except Exception as exc:
                print(f"Failed to fetch Sherdog recent events page: {exc}")
                break

            soup = BeautifulSoup(response.text, "html.parser")

            events_container = soup.find("div", id="recent_tab")
            if not events_container:
                print("Sherdog layout changed or content blocked: 'recent_tab' not found")
                break
            for tr in events_container.find_all("tr", itemtype="http://schema.org/Event"):
                try:
                    url_tag = tr.find("a", itemprop="url")
                    name_tag = tr.find("span", itemprop="name")
                    date_meta = tr.find("meta", itemprop="startDate")
                    location_td = tr.find("td", itemprop="location")

                    if not url_tag or not name_tag or not date_meta:
                        continue

                    event_url = urljoin(self.base_url, url_tag["href"]) if url_tag and url_tag.get("href") else ""
                    event_title = name_tag.text.strip() if name_tag else ""

                    start_raw = date_meta.get("content", "")
                    try:
                        dt = dateutil_parser.isoparse(start_raw)
                    except Exception:
                        # Last resort: try stdlib
                        dt = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    event_date = dt.astimezone(ZoneInfo("Europe/London"))

                    location = location_td.get_text(" ", strip=True) if location_td else ""

                    events.append(Event(
                        url=event_url,
                        title=event_title,
                        date=event_date,
                        location=location,
                        organizer="UFC",
                    ))
                except Exception as row_exc:
                    print(f"Skipping previous event row due to parse error: {row_exc}")

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

    def get_upcoming_ufc_events(self) -> List[Event]:
        """
        Scrapes every upcoming UFC event from Sherdog.
        Returns a list of events.
        """
        current_url = urljoin(self.base_url, "/organizations/Ultimate-Fighting-Championship-UFC-2")
        events = []

        try:
            response = self._get(current_url)
        except Exception as exc:
            print(f"Failed to fetch Sherdog upcoming events page: {exc}")
            return events
        soup = BeautifulSoup(response.text, "html.parser")

        events_container = soup.find("div", id="upcoming_tab")
        if not events_container:
            print("Sherdog layout changed or content blocked: 'upcoming_tab' not found")
            return events
        for tr in events_container.find_all("tr", itemtype="http://schema.org/Event"):
            try:
                url_tag = tr.find("a", itemprop="url")
                name_tag = tr.find("span", itemprop="name")
                date_meta = tr.find("meta", itemprop="startDate")
                location_td = tr.find("td", itemprop="location")

                if not url_tag or not name_tag or not date_meta:
                    continue

                event_url = urljoin(self.base_url, url_tag["href"]) if url_tag and url_tag.get("href") else ""
                event_title = name_tag.text.strip() if name_tag else ""

                start_raw = date_meta.get("content", "")
                try:
                    dt = dateutil_parser.isoparse(start_raw)
                except Exception:
                    dt = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                event_date = dt.astimezone(ZoneInfo("Europe/London"))

                location = location_td.get_text(" ", strip=True) if location_td else ""

                events.append(Event(
                    url=event_url,
                    title=event_title,
                    date=event_date,
                    location=location,
                    organizer="UFC",
                ))
            except Exception as row_exc:
                print(f"Skipping upcoming event row due to parse error: {row_exc}")
        
        return events
    
    def get_previous_event_fights(self, event_url: str) -> List[Fight]:
        """
        Scrapes the fights for a given previous event from Sherdog.
        Returns a list of fights.
        """
        try:
            response = self._get(event_url)
        except Exception as exc:
            print(f"Failed to fetch Sherdog event page for previous fights: {exc}")
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        fights = []

        main_event_container = soup.find("div", itemprop="subEvent")
        if main_event_container:
            fighter_1_container = main_event_container.find("div", class_="fighter left_side")
            fighter_2_container = main_event_container.find("div", class_="fighter right_side")

            fighter_1_link_rel = fighter_1_container.find("a", itemprop="url").get("href")
            fighter_2_link_rel = fighter_2_container.find("a", itemprop="url").get("href")

            fighter_1_url = (
                urljoin(self.base_url, fighter_1_link_rel)
                if self._is_valid_href(fighter_1_link_rel)
                else self.UNKNOWN_FIGHTER_URL
            )
            fighter_2_url = (
                urljoin(self.base_url, fighter_2_link_rel)
                if self._is_valid_href(fighter_2_link_rel)
                else self.UNKNOWN_FIGHTER_URL
            )

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

            match_number = int(
                "".join(filter(str.isdigit, resume_cells[0].get_text(strip=True)))
            )

            raw_method = resume_cells[1].get_text(" ", strip=True)
            fight_method = re.sub(r"^Method\s+", "", raw_method, flags=re.IGNORECASE)
            fight_round = int(
                "".join(filter(str.isdigit, resume_cells[3].get_text(strip=True)))
            )
            raw_time = resume_cells[4].get_text(strip=True)
            time_match = re.search(r"\d{1,2}:\d{2}", raw_time)
            fight_time = time_match.group(0) if time_match else ""

            fights.append(
                Fight(
                    event_url=event_url,
                    fighter_1_url=fighter_1_url,
                    fighter_2_url=fighter_2_url,
                    match_number=match_number,
                    weight_class=fight_weight,
                    winner=fight_winner,
                    method=fight_method,
                    round=fight_round,
                    time=fight_time,
                )
            )

        fight_card_container = soup.find("div", class_="new_table_holder")
        if not fight_card_container:
            return fights

        for tr in fight_card_container.find_all("tr", itemprop="subEvent"):
            tds = tr.find_all("td")

            match_number_text = tds[0].get_text(strip=True)
            match_number_val = int(''.join(filter(str.isdigit, match_number_text)))

            fighter_1_container = tds[1]
            fighter_2_container = tds[3]

            fighter_1_url_rel = fighter_1_container.find("a", itemprop="url")["href"]
            fighter_2_url_rel = fighter_2_container.find("a", itemprop="url")["href"]

            fighter_1_url = (
                urljoin(self.base_url, fighter_1_url_rel)
                if self._is_valid_href(fighter_1_url_rel)
                else self.UNKNOWN_FIGHTER_URL
            )
            fighter_2_url = (
                urljoin(self.base_url, fighter_2_url_rel)
                if self._is_valid_href(fighter_2_url_rel)
                else self.UNKNOWN_FIGHTER_URL
            )

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

            # Clean up method string as above
            raw_method_td = tds[4].find("b").get_text(" ", strip=True)
            fight_method = re.sub(r"^Method\s+", "", raw_method_td, flags=re.IGNORECASE)

            fight_round_val = int(
                "".join(filter(str.isdigit, tds[5].get_text(strip=True)))
            )

            raw_time_td = tds[6].get_text(strip=True)
            time_match_td = re.search(r"\d{1,2}:\d{2}", raw_time_td)
            fight_time = time_match_td.group(0) if time_match_td else ""

            fights.append(Fight(
                event_url=event_url,
                fighter_1_url=fighter_1_url,
                fighter_2_url=fighter_2_url,
                match_number=match_number_val,
                weight_class=fight_weight,
                winner=fight_winner,
                method=fight_method,
                round=fight_round_val,
                time=fight_time,
            ))

        return fights
    
    def get_upcoming_event_fights(self, event_url: str) -> List[Fight]:
        """
        Scrapes the fights for a given upcoming event from Sherdog.
        Returns a list of fights.
        """
        try:
            response = self._get(event_url)
        except Exception as exc:
            print(f"Failed to fetch Sherdog event page for upcoming fights: {exc}")
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        fights = []

        fight_card_container = soup.find("div", class_="new_table_holder")
        if fight_card_container:
            for tr in fight_card_container.find_all("tr", itemprop="subEvent"):
                tds = tr.find_all("td")

                match_number_text = tds[0].get_text(strip=True)
                match_number_val = int(''.join(filter(str.isdigit, match_number_text)))

                fighter_1_container = tds[1]
                fighter_2_container = tds[3]

                fighter_1_url_rel = fighter_1_container.find("a", itemprop="url")["href"]
                fighter_2_url_rel = fighter_2_container.find("a", itemprop="url")["href"]

                fighter_1_url = (
                    urljoin(self.base_url, fighter_1_url_rel)
                    if self._is_valid_href(fighter_1_url_rel)
                    else self.UNKNOWN_FIGHTER_URL
                )
                fighter_2_url = (
                    urljoin(self.base_url, fighter_2_url_rel)
                    if self._is_valid_href(fighter_2_url_rel)
                    else self.UNKNOWN_FIGHTER_URL
                )

                fight_weight = tds[2].find("span", class_="weight_class").text.strip()

                fights.append(Fight(
                    event_url=event_url,
                    fighter_1_url=fighter_1_url,
                    fighter_2_url=fighter_2_url,
                    match_number=match_number_val,
                    weight_class=fight_weight,
                    winner="",
                    method="",
                    round=0,
                    time="",
                ))


        main_event_container = soup.find("div", itemprop="subEvent")
        if main_event_container:
            fighter_1_container = main_event_container.find("div", class_="fighter left_side")
            fighter_2_container = main_event_container.find("div", class_="fighter right_side")

            fighter_1_url_rel = fighter_1_container.find("a", itemprop="url").get("href")
            fighter_2_url_rel = fighter_2_container.find("a", itemprop="url").get("href")

            fighter_1_url = (
                urljoin(self.base_url, fighter_1_url_rel)
                if self._is_valid_href(fighter_1_url_rel)
                else self.UNKNOWN_FIGHTER_URL
            )
            fighter_2_url = (
                urljoin(self.base_url, fighter_2_url_rel)
                if self._is_valid_href(fighter_2_url_rel)
                else self.UNKNOWN_FIGHTER_URL
            )

            fight_weight = main_event_container.find("span", class_="weight_class").text.strip()
            fights.append(
                Fight(
                    event_url=event_url,
                    fighter_1_url=fighter_1_url,
                    fighter_2_url=fighter_2_url,
                    match_number=len(fights) + 1,
                    weight_class=fight_weight,
                    winner="",
                    method="",
                    round=0,
                    time="",
                )
            )

        return fights
    
    def get_fighter_stats(self, fighter_url: str):
        """
        Scrapes the stats for a given fighter from Sherdog.
        Returns a Fighter object.
        """
        if fighter_url == self.UNKNOWN_FIGHTER_URL:
            return Fighter(
                url=self.UNKNOWN_FIGHTER_URL,
                name="Unknown Fighter",
                nickname="",
                image_url="",
                record="0-0-0, 0 NC",
                ranking="",
                country="",
                city="",
                dob=None,
                height="",
                weight_class="",
                association="",
            )
        response = self._get(fighter_url)
        soup = BeautifulSoup(response.text, "html.parser")

        name = strip_accents(soup.find("h1", itemprop="name").text.strip())
        nickname = soup.find("span", class_="nickname").text.strip() if soup.find("span", class_="nickname") else ""

        image_url = self.base_url + soup.find("img", itemprop="image")["src"]

        wins = re.search(r"\d+", soup.find("div", class_="winloses win").text.strip()).group(0)
        loses = re.search(r"\d+", soup.find("div", class_="winloses lose").text.strip()).group(0)
        draws = re.search(r"\d+", soup.find("div", class_="winloses draws").text.strip()).group(0) if soup.find("div", class_="winloses draws") else "0"
        no_contests = re.search(r"\d+", soup.find("div", class_="winloses nc").text.strip()).group(0) if soup.find("div", class_="winloses nc") else "0"
        record = f"{wins}-{loses}-{draws}, {no_contests} NC"

        country = soup.find("strong", itemprop="nationality").text.strip() if soup.find("strong", itemprop="nationality") else ""
        city = soup.find("span", itemprop="addressLocality", class_="locality").text.strip() if soup.find("span", itemprop="addressLocality", class_="locality") else ""

        bio_holder = soup.find("div", class_="bio-holder")
        bio_holder_trs = bio_holder.find_all("tr")

        dob_str = bio_holder_trs[0].find("span", itemprop="birthDate").text.strip() if bio_holder_trs[0].find("span", itemprop="birthDate") else ""
        dob = datetime.strptime(dob_str, "%b %d, %Y").date() if dob_str else None
        
        height = bio_holder_trs[1].find("b", itemprop="height").text.strip() if bio_holder_trs[1].find("b", itemprop="height") else ""
        
        weight_class_tag = bio_holder.select_one("div.association-class a[href*='weightclass=']")
        weight_class = weight_class_tag.text.strip() if weight_class_tag else ""

        association = bio_holder.find("span", itemprop="memberOf").text.strip() if bio_holder.find("span", itemprop="memberOf") else ""

        return Fighter(
            url=fighter_url,
            name=name,
            nickname=nickname,
            image_url=image_url,
            record=record,
            ranking="",
            country=country,
            city=city,
            dob=dob,
            height=height,
            weight_class=weight_class,
            association=association,
        )