from pydantic import BaseModel

class Fighter(BaseModel):
    id: int
    name: str
    nickname: str | None = None
    image_url: str | None = None
    record: str | None = None
    ranking: str | None = None
    country: str | None = None
    city: str | None = None
    dob: str | None = None
    height: str | None = None
    weight_class: str | None = None
    association: str | None = None

class FighterSearchResponse(BaseModel):
    fighters: list[Fighter]
    total: int