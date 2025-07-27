import cloudscraper
from bs4 import BeautifulSoup
from app.core.utils.string_utils import strip_accents

class UFCRankingScraper:
    def __init__(self):
        self.base_url = "https://www.ufc.com/rankings"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }

    def get_ufc_rankings(self) -> dict:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(self.base_url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        rankings = {
            "Strawweight": [],
            "Flyweight": [],
            "Bantamweight": [],
            "Featherweight": [],
            "Lightweight": [],
            "Welterweight": [],
            "Middleweight": [],
            "Light Heavyweight": [],
            "Heavyweight": [],
        }

        ranking_tables = soup.find_all("div", class_="view-grouping")

        for table in ranking_tables:
            header_div = table.find("div", class_="view-grouping-header")

            header_text = header_div.get_text(" ", strip=True)
            if "Pound-for-Pound" in header_text:
                continue

            weight_class = header_div.find(text=True, recursive=False).strip()

            if weight_class.startswith("Women's "):
                weight_class = weight_class.split(" ", 1)[1]

            caption_tag = table.find("caption")
            champion_header = caption_tag.find("h5")
            champion_name = strip_accents(champion_header.get_text(strip=True))

            if champion_name:
                rankings[weight_class].append((champion_name, "Champion"))
            
            tbody = table.find("tbody")

            for tr in tbody.find_all("tr"):
                rank = tr.find("td", class_="views-field-weight-class-rank").get_text(strip=True)
                name = strip_accents(tr.find("td", class_="views-field-title").get_text(strip=True))

                rankings[weight_class].append((name, rank))

        print(rankings)
        return rankings