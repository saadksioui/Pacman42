from pydantic import BaseModel, Field


class Score(BaseModel):
    score: int = Field(ge=0)
    owner: str = Field(min_length=0)
