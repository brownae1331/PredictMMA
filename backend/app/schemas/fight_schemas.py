from pydantic import BaseModel
from enum import Enum

class ResultType(str, Enum):
    WIN = "WIN"
    DRAW = "DRAW"
    NO_CONTEST = "NO_CONTEST"

class Fight(BaseModel):
    id: int
    fighter_1_id: int
    fighter_2_id: int
    fighter_1_name: str
    fighter_2_name: str
    fighter_1_image: str | None
    fighter_2_image: str | None
    fighter_1_ranking: str | None
    fighter_2_ranking: str | None
    fighter_1_flag: str
    fighter_2_flag: str
    weight_class: str
    winner: str | None
    method: str | None
    round: int | None
    time: str | None

class FightResult(BaseModel):
    result_type: ResultType
    winner_id: int | None
    method: str
    round: int
    time: str

class FighterFightHistory(BaseModel):
    id: int
    event_title: str
    event_date: str | None
    event_location: str | None
    opponent_id: int
    opponent_name: str
    opponent_image: str | None
    opponent_country: str | None
    opponent_flag: str | None
    weight_class: str | None
    result: str  # "Win", "Loss", "Draw", "No Contest", "N/A"
    method: str | None
    round: int | None
    time: str | None