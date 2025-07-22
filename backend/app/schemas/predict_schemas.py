from pydantic import BaseModel
from enum import Enum

class Method(str, Enum):
    KO = "KO"
    SUBMISSION = "SUBMISSION"
    DECISION = "DECISION"

class PredictionCreate(BaseModel):
    user_id: int
    fight_id: int
    fighter_id: int
    method: Method
    round: int | None

class PredictionOutMakePrediction(BaseModel):
    winner_id: int
    method: Method
    round: int | None

class PredictionOutPredict(BaseModel):
    event_title: str
    fighter_1_name: str
    fighter_2_name: str
    winner_image: str
    method: Method
    round: int | None