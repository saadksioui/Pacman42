import json
from pydantic import BaseModel, Field
from typing import List, Dict


class Config(BaseModel):
    seed: int = Field(gt=0)
    lives: int = Field(gt=0)
    level_max_time: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    highscore_filename: str
    levels: List[Dict[str, int]]


class ConfigParser:
    def __init__(self, file: str):
        self.file = file

    def generate(self):
        with open(self.file, 'r') as f:
            data = f.read()
        data_no_comments = ""
        lines = data.split("\n")
        for line in lines:
            no_space = line.strip()
            if no_space.startswith(('#', '//')):
                continue
            data_no_comments += f"{line}\n"
        data_no_comments = json.loads(data_no_comments)
        config = Config(**data_no_comments)
        return config