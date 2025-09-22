from pydantic import BaseModel
from enum import Enum
from datetime import datetime

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

class PredictionResult(BaseModel):
    fighter: bool
    method: bool
    round: bool

class PredictionOutPredict(BaseModel):
    event_title: str
    event_date: datetime
    fighter_1_name: str
    fighter_2_name: str
    winner_name: str
    method: Method
    round: int | None
    result: PredictionResult | None