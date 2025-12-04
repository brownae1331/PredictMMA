import requests
from bs4 import BeautifulSoup
from app.schemas.scraper_schemas import Fight

class UFCStatsFightScraper:
    def __init__(self, event_url: str):
        self.url = event_url
        self.scraper = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        }

    def get_fights(self) -> list[Fight]:
        fights = []
        response = self.scraper.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        fight_containers = soup.find_all("tr", class_="b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click")
        for i, fight_container in enumerate(fight_containers):
            match_number = i + 1
            
            cols = fight_container.find_all("td", class_="b-fight-details__table-col")
            
            winner_str = None
            first_col = cols[0] if len(cols) > 0 else None
            fighter_1_url = None
            fighter_2_url = None
            
            # Get fighter URLs first
            if len(cols) > 1:
                fighter_links = cols[1].find_all("a", class_="b-link b-link_style_black")
                if len(fighter_links) >= 2:
                    fighter_1_url = fighter_links[0].get("href")
                    fighter_2_url = fighter_links[1].get("href")
                elif len(fighter_links) == 1:
                    fighter_1_url = fighter_links[0].get("href")
            
            # Determine winner by checking for winner flags
            if first_col:
                # Check for draw or no contest first
                all_flags = first_col.find_all("a", class_="b-flag")
                for flag in all_flags:
                    flag_text = flag.get_text(strip=True).lower()
                    if "draw" in flag_text:
                        winner_str = "draw"
                        break
                    elif "no contest" in flag_text or "nc" in flag_text:
                        winner_str = "no contest"
                        break
                
                # If no draw/no contest, check for winner flag
                if not winner_str:
                    winner_flags = first_col.find_all("a", class_="b-flag b-flag_style_green")
                    if winner_flags:
                        for flag in winner_flags:
                            win_text = flag.find("i", class_="b-flag__text")
                            if win_text and "win" in win_text.get_text(strip=True).lower():
                                # For now, set winner to fighter_1 if there's a winner flag
                                # This matches the current implementation assumption
                                winner_str = "fighter_1"
                                break
            
            weight_class = None
            if len(cols) > 6:
                weight_class_text = cols[6].get_text(strip=True)
                if weight_class_text:
                    weight_class = weight_class_text.split('\n')[0].strip()
                    weight_class = weight_class if weight_class else None
            
            method = None
            if len(cols) > 7:
                method_paragraphs = cols[7].find_all("p", class_="b-fight-details__table-text")
                if method_paragraphs:
                    method_text = method_paragraphs[0].get_text(strip=True)
                    method = method_text if method_text else None
            
            round_num = None
            if len(cols) > 8:
                round_text = cols[8].get_text(strip=True)
                if round_text:
                    try:
                        round_num = int(round_text)
                    except ValueError:
                        round_num = None
            
            time = None
            if len(cols) > 9:
                time_text = cols[9].get_text(strip=True)
                time = time_text if time_text else None
            
            if fighter_1_url and fighter_2_url:
                fights.append(Fight(
                    event_url=self.url,
                    fighter_1_url=fighter_1_url,
                    fighter_2_url=fighter_2_url,
                    match_number=match_number,
                    weight_class=weight_class,
                    winner=winner_str,
                    method=method,
                    round=round_num,
                    time=time,
                ))
        
        return fights