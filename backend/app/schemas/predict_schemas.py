from pydantic import BaseModel

class Prediction(BaseModel):
    user_id: int
    event_url: str
    fight_idx: int
    fighter_prediction: str
    method_prediction: str
    round_prediction: int | None