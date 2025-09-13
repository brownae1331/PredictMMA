import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin
import re
from typing import Dict, List, Optional

class UFCEventDatetimeScraper:
    def __init__(self):
        self.base_url = "https://www.espn.co.uk"
        self.scraper = requests.Session()
        self.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    }

    def get_all_events_datetimes(self) -> Dict[str, datetime]:
        """
        Scrape all UFC events and their datetimes from ESPN UK from 2025 down to 1993.
        
        Returns:
            Dict[str, datetime]: Dictionary mapping event names to their datetime objects
        """
        all_events = {}
        
        # Loop through years from 2025 down to 1993
        for year in range(2025, 1992, -1):  # 1992 is exclusive, so it stops at 1993
            print(f"Scraping events for year {year}...")
            
            url = urljoin(self.base_url, f"/mma/schedule/_/year/{year}/league/ufc")
            
            try:
                response = self.scraper.get(url, headers=self.headers)
                
                if response.status_code != 200:
                    print(f"Warning: Failed to fetch page for year {year}: {response.status_code}")
                    continue
                    
                soup = BeautifulSoup(response.text, "html.parser")
                year_events = self._extract_event_datetimes(soup, year)
                
                # Add events from this year to the main dictionary
                all_events.update(year_events)
                print(f"Found {len(year_events)} events for year {year}")
                
            except Exception as e:
                print(f"Error scraping events for year {year}: {e}")
                continue
        
        print(f"Total events found: {len(all_events)}")
        return all_events
    
    def _extract_event_datetimes(self, soup: BeautifulSoup, year: int) -> Dict[str, datetime]:
        """
        Extract event datetimes from the parsed HTML.
        
        Args:
            soup: BeautifulSoup object of the parsed HTML
            year: The year being scraped
            
        Returns:
            Dict[str, datetime]: Dictionary mapping event names to their datetime objects
        """
        events = {}
        
        # Find all table bodies containing events
        tbodies = soup.find_all("tbody", class_="Table__TBODY")
        
        if not tbodies:
            return events
        
        # Process each table body
        for tbody in tbodies:
            # Find all event rows in this table body
            rows = tbody.find_all("tr", class_="Table__TR")
            
            for row in rows:
                event_data = self._parse_event_row(row, year)
                if event_data:
                    event_name, event_datetime = event_data
                    events[event_name] = event_datetime
                
        return events
    
    def _parse_event_row(self, row, year: int) -> Optional[tuple[str, datetime]]:
        """
        Parse a single event row to extract event name and datetime.
        
        Args:
            row: BeautifulSoup element representing a table row
            year: The year for this event
            
        Returns:
            Optional[tuple[str, datetime]]: Tuple of (event_name, datetime) or None if parsing fails
        """
        try:
            # Extract date from the first column
            date_cell = row.find("span", class_="date__innerCell")
            if not date_cell:
                return None
            date_text = date_cell.get_text(strip=True)
            
            # Try to extract time from the second column (time link)
            time_text = None
            time_cells = row.find_all("td", class_="date__col")
            if len(time_cells) >= 2:
                time_link = time_cells[1].find("a", class_="AnchorLink")
                if time_link:
                    time_text = time_link.get_text(strip=True)
            
            # Extract event name from the event column
            event_cell = row.find("td", class_="event__col")
            if not event_cell:
                return None
            
            event_link = event_cell.find("a", class_="AnchorLink")
            if not event_link:
                return None
            event_name = event_link.get_text(strip=True)
            
            # Parse datetime (with or without time)
            event_datetime = self._parse_datetime(date_text, time_text, year)
            if not event_datetime:
                return None
                
            return event_name, event_datetime
            
        except Exception as e:
            print(f"Error parsing event row: {e}")
            return None
    
    def _parse_datetime(self, date_text: str, time_text: Optional[str], year: int) -> Optional[datetime]:
        """
        Parse date and time strings into a datetime object.
        
        Args:
            date_text: Date string like "13 Sep"
            time_text: Time string like "8:00 PM" or None if no time available
            year: The year for this event
            
        Returns:
            Optional[datetime]: Parsed datetime object or None if parsing fails
        """
        try:
            
            # Parse date (format: "13 Sep")
            date_parts = date_text.split()
            if len(date_parts) != 2:
                return None
                
            day = int(date_parts[0])
            month_abbr = date_parts[1]
            
            # Map month abbreviations to numbers
            months = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            
            month = months.get(month_abbr)
            if not month:
                return None
            
            # Default time values (used when time_text is None)
            hour = 20  # 8 PM default (typical UFC main card time)
            minute = 0
            
            # Parse time if available (format: "8:00 PM" or "1:00 AM")
            if time_text:
                time_match = re.match(r'^(\d{1,2}):(\d{2})\s*(AM|PM)$', time_text.upper())
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2))
                    am_pm = time_match.group(3)
                    
                    # Convert to 24-hour format
                    if am_pm == 'PM' and hour != 12:
                        hour += 12
                    elif am_pm == 'AM' and hour == 12:
                        hour = 0
                else:
                    # If time_text exists but doesn't match expected format, 
                    # still use default time rather than failing
                    print(f"Warning: Could not parse time '{time_text}', using default time")
            
            # Create datetime object
            # Note: This assumes UK timezone since we're scraping from ESPN UK
            event_datetime = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
            
            return event_datetime
            
        except Exception as e:
            print(f"Error parsing datetime '{date_text}' '{time_text}': {e}")
            return None


def main():
    """Example usage of the UFC Event Datetime Scraper - gets all events from 1993-2025."""
    scraper = UFCEventDatetimeScraper()
    
    try:
        # Get page to check table structure (using 2025 as example)
        url = scraper.base_url + "/mma/schedule/_/year/2025/league/ufc"
        response = scraper.scraper.get(url, headers=scraper.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Debug: Check how many table bodies exist
        tbodies = soup.find_all("tbody", class_="Table__TBODY")
        print(f"Found {len(tbodies)} table bodies on the 2025 page")
        
        # Get events
        events = scraper.get_all_events_datetimes()
        
        print(f"Found {len(events)} total UFC events (1993-2025):")
        print("-" * 80)
        
        for event_name, event_datetime in sorted(events.items(), key=lambda x: x[1]):
            print(f"Event: {event_name}")
            print(f"Datetime: {event_datetime.strftime('%Y-%m-%d %H:%M UTC')}")
            # Note: Events without specific times use default time of 20:00 UTC (8 PM)
            print("-" * 80)
            
    except Exception as e:
        print(f"Error scraping events: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()