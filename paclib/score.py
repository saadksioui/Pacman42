from pydantic import BaseModel, Field


class Score(BaseModel):
    """Represents a validated highscore entry with player owner and points."""
    score: int = Field(ge=0)
    owner: str = Field(min_length=0)
