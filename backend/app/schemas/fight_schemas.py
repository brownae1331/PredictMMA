from pydantic import BaseModel
from app.schemas.predict_schemas import Method
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
    fighter_1_image: str
    fighter_2_image: str
    fighter_1_ranking: str | None
    fighter_2_ranking: str | None
    fighter_1_flag: str
    fighter_2_flag: str
    weight_class: str
    winner: str
    method: Method
    round: int
    time: str

class FightResult(BaseModel):
    result_type: ResultType
    winner_id: int | None
    method: Method
    round: int
    time: str