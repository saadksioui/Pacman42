from pydantic import BaseModel, Field
import random


class Level(BaseModel):
    width: int = 300
    height: int = 300
    level_max_time: int = 90


class Config(BaseModel):
    highscore_path: str = "scores.json"
    levels: list[Level] = Field(
        default=[Level() for _ in range(10)],
        min_length=10
    )
    lives: int = 3
    pacgum: int = 42
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = random.randint(0, 10**10)


if __name__ == "__main__":
    c = Config.model_validate({})

    print(c.levels)
