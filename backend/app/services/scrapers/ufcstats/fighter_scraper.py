import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.schemas.scraper_schemas import Fighter

class UFCStatsFighterScraper:
    def __init__(self):
        self.base_url = "http://ufcstats.com/statistics/fighters"
        self.scraper = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }

    def get_all_fighters(self) -> list[Fighter]:
        fighters = []
        for i in range(ord('a'), ord('z') + 1):
            print(f"Scraping fighters starting with {chr(i)}")
            url = urljoin(self.base_url, f"?char={chr(i)}&page=all")
            response = self.scraper.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")

            fighter_containers = soup.find_all("tr", class_="b-statistics__table-row")
            for fighter in fighter_containers:
                cols = fighter.find_all("td", class_="b-statistics__table-col")
                if len(cols) < 10:
                    continue
                
                first_link = cols[0].find("a")
                if not first_link or not first_link.get("href"):
                    continue
                
                url = first_link["href"]
                
                first_name = cols[0].get_text(strip=True)
                last_name = cols[1].get_text(strip=True)
                name = f"{first_name} {last_name}".strip()
                
                if not name:
                    continue
                
                nickname = cols[2].get_text(strip=True) or None
                
                height = cols[3].get_text(strip=True)
                height = height if height and height != "--" else None
                
                weight = cols[4].get_text(strip=True)
                weight = weight if weight and weight != "--" else None
                
                reach = cols[5].get_text(strip=True)
                reach = reach if reach and reach != "--" else None
                
                stance = cols[6].get_text(strip=True) or None
                
                try:
                    wins = int(cols[7].get_text(strip=True)) if cols[7].get_text(strip=True) else 0
                except (ValueError, IndexError):
                    wins = 0
                
                try:
                    losses = int(cols[8].get_text(strip=True)) if cols[8].get_text(strip=True) else 0
                except (ValueError, IndexError):
                    losses = 0
                
                try:
                    draws = int(cols[9].get_text(strip=True)) if cols[9].get_text(strip=True) else 0
                except (ValueError, IndexError):
                    draws = 0
                
                fighters.append(Fighter(
                    url=url,
                    name=name,
                    nickname=nickname,
                    height=height,
                    weight=weight,
                    reach=reach,
                    stance=stance,
                    wins=wins,
                    losses=losses,
                    draws=draws,
                ))
        
        return fighters