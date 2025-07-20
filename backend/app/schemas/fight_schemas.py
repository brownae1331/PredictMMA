from pydantic import BaseModel

class Fight(BaseModel):
    fighter_1_id: int
    fighter_2_id: int
    fighter_1_name: str
    fighter_2_name: str
    fighter_1_image: str
    fighter_2_image: str
    fighter_1_ranking: str | None
    fighter_2_ranking: str | None
    fighter_1_flag: str
    fighter_2_flag: str
    match_number: int
    weight_class: str
    winner: str
    method: str
    round: int
    time: str