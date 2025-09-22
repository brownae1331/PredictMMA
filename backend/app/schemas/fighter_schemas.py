from pydantic import BaseModel

class Fighter(BaseModel):
    id: int
    name: str
    nickname: str
    image_url: str
    record: str
    ranking: str
    country: str
    city: str
    dob: str | None
    height: str
    weight_class: str
    association: str

class FighterSearchResponse(BaseModel):
    fighters: list[Fighter]
    total: int